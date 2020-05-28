import os
import glob
import pandas as pd
import argparse
import math
from shutil import copyfile
import xml.etree.ElementTree as ET
import random
from xml.dom import minidom

def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='\t')

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def move(filename, save_dir):
    splited_path = filename.split(os.sep)
    new_filename = splited_path[-3] + "_" + splited_path[-1]
    copyfile(filename, os.path.join(save_dir, new_filename))
    xml_file = os.path.splitext(filename)[0]+'.xml'
    tree = ET.parse(xml_file)
    root = tree.getroot()
    link = root.find('filename')
    link.text = new_filename
    prettify(root)
    indent(root)
    tree.write(os.path.join(save_dir, os.path.splitext(new_filename)[0]+'.xml'))

def gather(inputDir, outputDir, ratio):
    train_dir = os.path.join(outputDir, 'train')
    test_dir = os.path.join(outputDir, 'test')

    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    images = []
    for folder in glob.glob(inputDir + "/*"):
        for image in glob.glob(folder + "/images/*.jpg"):
            images.append(image)
        
    num_images = len(images)
    num_test_images = math.ceil(ratio*num_images)

    for i in range(num_test_images):
        idx = random.randint(0, len(images)-1)
        filename = images[idx]
        move(filename, test_dir)
        images.remove(images[idx])

    for filename in images:
        move(filename, train_dir)
        
    print(num_images, num_test_images)


def main():
    parser = argparse.ArgumentParser(description="It's gathering data from different folders")
    parser.add_argument(
        "-i",
        "--inputDir",
        type=str
    )
    parser.add_argument(
        "-o",
        "--outputDir",
        type=str
    )
    parser.add_argument(
        '-r', '--ratio',
        help='The ratio of the number of test images over the total number of images. The default is 0.1.',
        default=0.1,
        type=float
    )
    args = parser.parse_args()

    assert(os.path.isdir(args.inputDir))
    assert(os.path.isdir(args.outputDir))

    gather(args.inputDir, args.outputDir, args.ratio)
    print("Successfully gathered data.")

if __name__ == '__main__':
    main()