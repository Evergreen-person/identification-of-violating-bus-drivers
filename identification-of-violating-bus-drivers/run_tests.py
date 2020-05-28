import argparse
import json
import os
import glob
from algorithm import scan_video


def parse_config(file):
    with open(file, 'r') as conf:
        data = conf.read()
    return json.loads(data)


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
             person_count_to_be_tracked_after_crossed,
             person_nn_age):

    print(f'[INFO] run test for {input}')
    events = scan_video(input,
                        output + '_test.avi',
                        False,
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
                        person_nn_age)

    with open(output + '.txt', 'a') as file:
        for event in events:
            print(f'[INFO][EVENT] {event.message()}')
            file.write(f'{int(event.frame_id)} {event.message()}\n')
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
    args = parser.parse_args()
    conf = parse_config(args.config)
    video_conf = conf['format_video_to_save']
    bus_conf = conf['bus']
    person_conf = conf['person']
    deep_sort_conf = conf['deep_sort']
    for video in glob.glob(args.path + "/*.asf"):
        run_test(video,
                 os.path.join(args.path, os.path.splitext(video)[0]),
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


if __name__ == "__main__":
    main()
