import json
import numpy as np
import requests
import cv2
from PIL import Image
import argparse
import tensorflow as tf
from addons.deep_sort.deep_sort.detection import Detection as ddet
from addons.deep_sort.application_util import preprocessing
from addons.deep_sort.deep_sort import nn_matching
from addons.deep_sort.deep_sort.detection import Detection
from addons.deep_sort.deep_sort.tracker import Tracker
from addons.deep_sort.tools import generate_detections as gdet
from addons.deep_sort.deep_sort.detection import Detection as ddet
from utils.model_connector import predict, reshape_boxes
from collections import deque
import warnings
from math import hypot
import json
from shapely.geometry import box
from predictor import Predictor
from bus import Bus
from person import Person
from tracked import Tracked
from functools import partial

import sys
warnings.filterwarnings(action='once')

BUS_CLASS = 1
PERSON_CLASS = 2
COLORS = np.random.randint(0, 255, size=(200, 3), dtype="uint8")


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


def draw_legend(frame, tracked, last_points=40):
    for track in tracked.tracker.tracks:
        if track.is_confirmed() and not track.time_since_update > 0:
            bbox = track.to_tlbr()
            color = [int(c) for c in COLORS[track.track_id]]
            cv2.rectangle(frame, (int(bbox[0]), int(
                bbox[1])), (int(bbox[2]), int(bbox[3])), (color), 3)
            cv2.putText(frame, f'{tracked.name}_{track.track_id}', (int(bbox[0]), int(
                bbox[1] - 10)), 0, 5e-3 * 100, (color), 2)

            centers_length = len(tracked.values[track.track_id].centers)
            pts = tracked.values[track.track_id].centers
            for i in range(max([1, centers_length - last_points]), centers_length):
                if pts[i - 1] is None or pts[i] is None:
                    continue
                thickness = int(
                    np.sqrt(64 / float(i - centers_length + last_points + 1)) * 2)
                cv2.line(frame, (pts[i-1]),
                         (pts[i]), (color), thickness)


def draw_events(frame, frame_id, events, per_last_frames=100):
    i = 0
    for event in events:
        if event.frame_id + per_last_frames > frame_id:
            cv2.putText(frame, event.message(),
                        (50, 50 + 50*i), 0, 0.5, (0, 255, 0), 2)
            i += 1


def write_events(output, events):
    with open(output, 'a') as file:
        for event in events:
            file.write(f'{int(event.frame_id)} {event.message()}\n')


def scan_video(
        input,
        output,
        is_show,
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
        person_count_to_be_tracked_after_crossed,
        person_nn_age):

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
        out = cv2.VideoWriter(output, fourcc, fps, (video_width, video_height))
        frame_index = -1

    frame_id = -1

    tracked_buses = Tracked('BUS',
                            deep_sort_model_filename,
                            deep_sort_max_cosine_distance,
                            None,
                            partial(Bus,
                                    counter_to_change_state=bus_count_to_change_state,
                                    min_distance=bus_min_distance,
                                    last_points=bus_distance_per_sec * fps,
                                    age=bus_nn_age))
    tracked_persons = Tracked('PERSON',
                              deep_sort_model_filename,
                              deep_sort_max_cosine_distance,
                              None,
                              partial(Person,
                                      last_points=50,
                                      is_show=False,
                                      count_to_be_shown=person_count_to_be_tracked_after_crossed,
                                      age=person_nn_age))

    while True:
        ok, frame = video.read()
        if not ok:
            break
        frame_id = frame_id + 1

        prediction = predictor(frame)
        bus_boxes, bus_scores, person_boxes, person_scores = split_to_buses_and_persons(
            prediction, min_confidence, width, heigth)

        tracked_buses.update(frame, bus_boxes, bus_scores, frame_id)
        tracked_persons.update(frame, person_boxes, person_scores, frame_id)

        for btrack in tracked_buses.tracker.tracks:
            if tracked_buses.values[btrack.track_id].is_stopped:
                bxmin, bymin, bxmax, bymax = btrack.to_tlbr()
                brect = box(bxmin, bymin, bxmax, bymax)
                for ptrack in tracked_persons.tracker.tracks:
                    if not ptrack.time_since_update > 0:
                        pxmin, pymin, pxmax, pymax = ptrack.to_tlbr()
                        if box(pxmin, pymin, pxmax, pymax).intersects(brect) and (pymax < bymax + (bymax - bymin) * 0.1):
                            tracked_persons.values[ptrack.track_id].set_crossed(
                                btrack.track_id, frame_id)

        tracked_persons.tick()
        tracked_buses.tick()

        if output or is_show:
            events = tracked_persons.events()
            events.extend(tracked_buses.events())

            draw_events(frame, frame_id, events)
            draw_legend(frame, tracked_persons)
            draw_legend(frame, tracked_buses)

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

    return events


def parse_config(file):
    with open(file, 'r') as conf:
        data = conf.read()
    return json.loads(data)


def main():
    parser = argparse.ArgumentParser(
        description="IT MAKES MIRACLE")
    parser.add_argument(
        "-i",
        "--input",
        help='Path to vidio file',
        type=str
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str
    )
    parser.add_argument(
        "--show",
        default=False,
        type=bool
    )
    parser.add_argument(
        '--config',
        help='Configuration file in JSON',
        required=True
    )
    parser.add_argument(
        '--log'
    )
    args = parser.parse_args()
    conf = parse_config(args.config)
    video_conf = conf['format_video_to_save']
    bus_conf = conf['bus']
    person_conf = conf['person']
    deep_sort_conf = conf['deep_sort']
    events = scan_video(args.input,
                        args.output,
                        args.show,
                        conf['model_filename'],
                        conf['min_confidence'],
                        video_conf['fps'],
                        video_conf['width'],
                        video_conf['height'],
                        deep_sort_conf['max_cosine_distance'],
                        deep_sort_conf['model_filename'],
                        bus_conf['count_to_change_state'],
                        bus_conf["min_distance"],
                        bus_conf["distance_per_sec"],
                        bus_conf["nn_age"],
                        person_conf['count_to_be_tracked_after_crossed'],
                        person_conf['nn_age'])

    if args.log:
        write_events(args.log, events)


if __name__ == '__main__':
    main()
