import json
import numpy as np
import cv2
import argparse
import tensorflow as tf
import warnings
from math import hypot
from shapely.geometry import box, Polygon
from predictor import Predictor
from bus import Bus
from person import Person
from tracked import Tracked
from functools import partial
from utils import *

import sys
warnings.filterwarnings(action='once')

BUS_CLASS = 1
PERSON_CLASS = 2


def split_to_buses_and_persons(prediction, min_score, width, heigth):
    num_detections = int(prediction['num_detections'])
    boxes = prediction['detection_boxes'][:num_detections]
    confidence = prediction['detection_scores'][:num_detections]
    detection_classes = prediction['detection_classes'][:num_detections]

    reshaped_boxes = reshape_boxes(boxes, width, heigth)
    bus_boxes = []
    bus_scores = []
    person_boxes = []
    person_scores = []
    for bbox, score, clazz in zip(reshaped_boxes, confidence, detection_classes):
        if score > min_score:
            if clazz == PERSON_CLASS:
                person_boxes.append(bbox)
                person_scores.append(score)
            elif clazz == BUS_CLASS:
                bus_boxes.append(bbox)
                bus_scores.append(score)
            else:
                raise ValueError('Unknown class: ' + str(clazz))
    return bus_boxes, bus_scores, person_boxes, person_scores

def belongsToBusStop(part, stops, w, h):
    for stop in stops:
        points = [(int(x*w),int(h*y)) for x, y in zip(stop['xpoints'], stop['ypoints'])]
        if Polygon(points).intersects(part):
            return True
    return False


def scan_video(
        input,
        output,
        is_show,
        skip_frames,
        model_filename,
        min_confidence,
        video_fps,
        video_width,
        video_height,
        deep_sort_max_cosine_distance,
        deep_sort_model_filename,
        bus_count_to_change_state,
        bus_min_distance,
        bus_distance_per_sec,
        bus_nn_age,
        bus_zoom_in_x,
        bus_bottom_part,
        person_nn_age,
        geometry):

    predictor = Predictor(model_filename)

    video = cv2.VideoCapture(input)
    if not video.isOpened():
        print("Could not open video")
        sys.exit()

    fps = 25  # video.get(cv2.CAP_PROP_FPS) is not work
    width = int(video.get(3))
    heigth = int(video.get(4))

    if output:
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        out = cv2.VideoWriter(output, fourcc, 5, (video_width, video_height))
        frame_index = -1

    frame_id = -1

    tracked_buses = Tracked('BUS',
                            deep_sort_model_filename,
                            deep_sort_max_cosine_distance,
                            None,
                            partial(Bus,
                                    counter_to_change_state=bus_count_to_change_state,
                                    min_distance=bus_min_distance,
                                    dist_persec=bus_distance_per_sec,
                                    nn_age=bus_nn_age,
                                    fps=fps))
    tracked_persons = Tracked('PERSON',
                              deep_sort_model_filename,
                              deep_sort_max_cosine_distance,
                              None,
                              partial(Person,
                                      fps=fps,
                                      nnage=person_nn_age))

    roads = []
    for road in geometry['roads']:
        points = [(int(x*width),int(heigth*y)) for x, y in zip(road['xpoints'], road['ypoints'])]
        roads.append(Polygon(points))

    skip_counter = 4
    while True:
        ok, frame = video.read()
        if not ok:
            break
        frame_id = frame_id + 1

        if frame_id < skip_frames:
            continue

        if skip_counter != 0:
            skip_counter -= 1
            continue
        else:
            skip_counter = 4

        prediction = predictor(frame)
        bus_boxes, bus_scores, person_boxes, person_scores = split_to_buses_and_persons(
            prediction, min_confidence, width, heigth)

        tracked_buses.update(frame, bus_boxes, bus_scores, frame_id)
        tracked_persons.update(frame, person_boxes, person_scores, frame_id)

        for btrack in tracked_buses.tracker.tracks:
            if tracked_buses.values[btrack.track_id].is_stopped:
                bxmin, bymin, bxmax, bymax = btrack.to_tlbr()
                scale = (bxmax - bxmin) * bus_zoom_in_x
                brect = box(bxmin - scale, bymin, bxmax + scale, bymax)
                downbrect = box(bxmin, bymax - (bymax - bymin)*0.1, bxmax, bymax)
                belongsToRoadIndex = np.argmax([downbrect.intersection(road).area for road in roads])
                for ptrack in tracked_persons.tracker.tracks:
                    if not ptrack.time_since_update > 0:
                        pxmin, pymin, pxmax, pymax = ptrack.to_tlbr()
                        downprect = box(pxmin, pymax - (pymax - pymin)*0.1, pxmax, pymax)                    
                        if box(pxmin, pymin, pxmax, pymax).intersects(brect) and \
                            (pymax < bymax) and \
                            (pymax > bymax - (bymax - bymin) * bus_bottom_part) and \
                            not belongsToBusStop(downprect, geometry['bus_stops'], width, heigth):
                            tracked_persons.values[ptrack.track_id].set_crossed(
                                btrack.track_id, frame_id, geometry['roads'][belongsToRoadIndex]['doors'])

        tracked_persons.tick()
        tracked_buses.tick()

        if output or is_show:
            events = tracked_persons.events()
            events.extend(tracked_buses.events())

            draw_events(frame, frame_id, events)
            draw_legend(frame, tracked_persons)
            draw_legend(frame, tracked_buses)
            draw_geometry(frame, geometry, width, heigth)

            frame = cv2.resize(frame, (video_width, video_height), fx=0, fy=0,
                               interpolation=cv2.INTER_CUBIC)
        if output:
            out.write(frame)
            frame_index = frame_index + 1
        if is_show:
            cv2.imshow("Tracking", frame)
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    video.release()
    if output:
        out.release()
    cv2.destroyAllWindows()

    events = tracked_persons.events()
    # events.extend(tracked_buses.events())
    del predictor
    del tracked_buses
    del tracked_persons
    return events
