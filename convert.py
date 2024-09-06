import os
from PIL import Image
import shutil
from voc_coco_conv import voc_to_coco, coco_to_voc
from yolo_coco_conv import coco_to_yolo, yolo_to_coco
from yolo_voc_conv import yolo_to_voc, voc_to_yolo

def convert_subset(input_dir, image_dir, class_list, output_dir, conversion_type):
    # Create output directories
    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'annotations' if conversion_type == 'yolo2voc' else 'labels'), exist_ok=True)

    # Process each annotation file
    for filename in os.listdir(input_dir):
        if (conversion_type == 'yolo2voc' and filename.endswith('.txt')) or (conversion_type == 'voc2yolo' and filename.endswith('.xml')):
            input_file = os.path.join(input_dir, filename)
            image_file = os.path.join(image_dir, os.path.splitext(filename)[0] + '.png')
            if not os.path.exists(image_file):
                image_file = os.path.join(image_dir, os.path.splitext(filename)[0] + '.jpeg')
            if os.path.exists(image_file):
                # Convert annotation
                if conversion_type == 'yolo2voc':
                    yolo_to_voc(input_file, image_file, class_list, output_dir)
                else:
                    voc_to_yolo(input_file, image_file, class_list, output_dir)
                
                # Copy image to new directory
                shutil.copy2(image_file, os.path.join(output_dir, 'images'))
                
                print(f"Converted and copied {filename}")
            else:
                print(f"Image not found for {filename}")

def convert_dataset(base_dir, class_file, output_base_dir, conversion_type):
    # Read class list
    with open(class_file, 'r') as f:
        class_list = [line.strip() for line in f.readlines()]
    subset_exist=False
    # Process each subset
    for subset in ['train', 'val', 'test']:
        input_dir = os.path.join(base_dir, subset, 'labels' if conversion_type == 'yolo2voc' else 'annotations')
        image_dir = os.path.join(base_dir, subset, 'images')
        output_dir = os.path.join(output_base_dir, subset)

        if os.path.exists(input_dir) and os.path.exists(image_dir):
            subset_exist=True
            print(f"Processing {subset} subset...")
            convert_subset(input_dir, image_dir, class_list, output_dir, conversion_type)
        else:
            print(f"Skipping {subset} subset: directory not found")
    if subset_exist==False:
        # convert without subsets
        input_dir = os.path.join(base_dir, 'labels' if conversion_type == 'yolo2voc' else 'annotations')
        image_dir = os.path.join(base_dir, 'images')
        output_dir = os.path.join(output_base_dir, subset)
        if os.path.exists(input_dir) and os.path.exists(image_dir):
            convert_subset(input_dir, image_dir, class_list, output_dir, conversion_type)