import pandas as pd
import numpy as np
import glob 
import os
import argparse

def stat(ground_truth_file, gain_result_file):
    TP = 0
    FN = 0
    FP = 0
    all_cases = 0
    gain_result = pd.read_csv(gain_result_file)
    grouped = gain_result.groupby('bus_id').agg({'frame' : [np.min, np.max]})
    ground_truth = pd.read_csv(ground_truth_file)
    handled = []
    for _, grow in ground_truth.iterrows():
        saved_count = grow['count']
        all_cases += saved_count
        count = 0
        for index, row in grouped.iterrows():
            #if (row[('frame', 'amin')] >= grow['frame_start']) and (row[('frame', 'amax')] <= grow['frame_end']):
            if (row[('frame', 'amin')] >= grow['frame_start']) and (row[('frame', 'amin')] <= grow['frame_end']) or \
                (row[('frame', 'amax')] >= grow['frame_start']) and (row[('frame', 'amax')] <= grow['frame_end']):
                count += 1
                handled.append(index)
        TP += min([saved_count, count])
        FP += max([0, count - saved_count])
        FN += max([0, saved_count - count])
    FP += grouped.loc[~grouped.index.isin(handled), :].shape[0]
    return (TP, FP, FN, all_cases)

def main():
    parser = argparse.ArgumentParser(description="IT TESTS THE MIRACLES")
    parser.add_argument(
        "-p",
        "--path",
        help='Path to test videos',
        type=str
    )
    parser.add_argument(
        '--output',
        required=True
    )
    args = parser.parse_args()
    values = []
    for folder in glob.glob(args.path + "*"):
        annotation = os.path.join(folder, 'annotation.csv')
        result = os.path.join(folder, os.path.split(folder)[-1]) + '.csv'
        if (os.path.isfile(annotation)) and (os.path.isfile(result)):
            tp, fp, fn, all_cases = stat(annotation, result)
            values.append((folder, int(tp), int(fp), int(fn), int(all_cases)))
    
    df = pd.DataFrame(values, columns=['Filename', 'TP', 'FP', 'FN', 'All'])
    df.to_csv(f"{args.output}", index=None)

if __name__ == "__main__":
    main()

