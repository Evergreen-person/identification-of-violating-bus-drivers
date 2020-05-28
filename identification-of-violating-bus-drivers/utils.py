import cv2
import numpy as np
import json


COLORS = np.random.randint(0, 255, size=(200, 3), dtype="uint8")


def reshape_boxes(boxes, width, heigth):
    return [(xmin * width, ymin * heigth, (xmax - xmin) * width, (ymax - ymin) * heigth) for (ymin, xmin, ymax, xmax) in boxes]


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


def parse_config(file):
    with open(file, 'r') as conf:
        data = conf.read()
    return json.loads(data)
