from utils import parse_config, write_events
from algorithm import scan_video
import argparse

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
    parser.add_argument(
        '--skip',
        help='Skip first N frames',
        required=False,
        default=0
    )
    args = parser.parse_args()
    conf = parse_config(args.config)
    geometry = parse_config(conf['geometry_filename'])
    video_conf = conf['format_video_to_save']
    bus_conf = conf['bus']
    person_conf = conf['person']
    deep_sort_conf = conf['deep_sort']
    events = scan_video(args.input,
                        args.output,
                        args.show,
                        args.skip,
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

    if args.log:
        write_events(args.log, events)


if __name__ == '__main__':
    main()