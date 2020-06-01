import argparse
import os
import glob
from algorithm import scan_video
from utils import parse_config
import pandas as pd
from analitics import stat

COLUMN_NAMES = ['frame', 'bus_id', 'message']


def run_test(input,
             output,
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

    print(f'[INFO] run test for {input}')
    events = scan_video(input,
                        False,
                        False,
                        0,
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
                        geometry)

    values = []
    for event in events:
        print(f'[INFO][EVENT] {event.message()}')
        values.append((int(event.frame_id), int(
            event.opposite_track_id), event.message()))
    df = pd.DataFrame(values, columns=COLUMN_NAMES)
    df.to_csv(f"{output}.csv", index=None)
    print(f'[INFO] run test for {input} is end')


def main():
    parser = argparse.ArgumentParser(description="IT TESTS THE MIRACLES")
    parser.add_argument(
        "-p",
        "--path",
        help='Path to test videos',
        type=str
    )
    parser.add_argument(
        '--config',
        help='Configuration file in JSON',
        required=True
    )
    parser.add_argument(
        '--output',
        required=True
    )
    args = parser.parse_args()
    conf = parse_config(args.config)
    video_conf = conf['format_video_to_save']
    bus_conf = conf['bus']
    person_conf = conf['person']
    deep_sort_conf = conf['deep_sort']
    geometry = parse_config(conf['geometry_filename'])
    TP = 0
    FP = 0
    FN = 0
    ALL = 0
    values = []
    all_folders = len(glob.glob(args.path + "*"))
    i = 1
    for folder in glob.glob(args.path + "*"):
        print(f'Start test for {i}/{all_folders}...')
        i += 1
        video = os.path.join(folder, os.path.split(folder)[-1] + ".asf")
        annotation = os.path.join(folder, 'annotation.csv')
        if os.path.isfile(video) and os.path.isfile(annotation):
            run_test(video,
                     os.path.join(folder, os.path.split(folder)[-1]),
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
                     bus_conf["zoom_in_x"],
                     bus_conf["bottom_part"],
                     person_conf['nn_age'],
                     geometry)
            tp, fp, fn, all_cases = stat(annotation, os.path.join(
                folder, os.path.split(folder)[-1]) + '.csv')
            values.append((video, int(tp), int(fp), int(fn), int(all_cases)))
            TP += tp
            FP += fp
            FN += fn
            ALL += all_cases

    print(f'result: TP={TP}, FP={FP}, FN={FN} ALL={ALL}')
    df = pd.DataFrame(values, columns=['Filename', 'TP', 'FP', 'FN', 'All'])
    df.to_csv(f"{args.output}.csv", index=None)


if __name__ == "__main__":
    main()
