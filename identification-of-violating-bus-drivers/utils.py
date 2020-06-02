import cv2
import numpy as np
import json


COLORS = np.random.randint(0, 255, size=(200, 3), dtype="uint8")


def reshape_boxes(boxes, width, heigth):
    return [(xmin * width, ymin * heigth, (xmax - xmin) * width, (ymax - ymin) * heigth) for (ymin, xmin, ymax, xmax) in boxes]


def draw_legend(frame, tracked, last_points=40):
    for track in tracked.tracker.tracks:
        if not track.time_since_update > 0:
            bbox = track.to_tlbr()
            color = [int(c) for c in COLORS[track.track_id % 200]]
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


def draw_events(frame, frame_id, events, per_last_frames=400):
    i = 0
    for event in events:
        if event.frame_id + per_last_frames > frame_id:
            cv2.putText(frame, event.message(),
                        (50, 50 + 50*i), 0, 0.5, (0, 255, 0), 2)
            i += 1


def draw_polygon(frame, items, w, h):
    for item in items:
        points = [(int(x*w), int(h*y))
                  for x, y in zip(item['xpoints'], item['ypoints'])]
        cv2.line(frame, points[0], points[1], (0, 255, 0), 2)
        cv2.line(frame, points[1], points[2], (0, 255, 0), 2)
        cv2.line(frame, points[2], points[3], (0, 255, 0), 2)
        cv2.line(frame, points[3], points[0], (0, 255, 0), 2)


def draw_geometry(frame, geometry, w, h):
    draw_polygon(frame, geometry['roads'], w, h)
    draw_polygon(frame, geometry['bus_stops'], w, h)


def write_events(output, events):
    with open(output, 'a') as file:
        for event in events:
            file.write(f'{int(event.frame_id)} {event.message()}\n')


def get_center(xmin, ymin, w, h):
    return (int((xmin+w)/2), int((ymin+h)/2))


def parse_config(file):
    with open(file, 'r') as conf:
        data = conf.read()
    return json.loads(data)
