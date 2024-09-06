import os
import xml.etree.ElementTree as ET
from PIL import Image
import shutil

def yolo_to_voc(yolo_file, image_file, class_list, output_dir):
    # Read YOLO file
    with open(yolo_file, 'r') as f:
        lines = f.readlines()

    # Get image dimensions
    img = Image.open(image_file)
    img_width, img_height = img.size

    # Create XML structure
    root = ET.Element("annotation")
    ET.SubElement(root, "folder").text = "images"
    ET.SubElement(root, "filename").text = os.path.basename(image_file)
    
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(img_width)
    ET.SubElement(size, "height").text = str(img_height)
    ET.SubElement(size, "depth").text = str(len(img.getbands()))

    for line in lines:
        class_id, x_center, y_center, width, height = map(float, line.strip().split())
        
        xmin = int((x_center - width/2) * img_width)
        xmax = int((x_center + width/2) * img_width)
        ymin = int((y_center - height/2) * img_height)
        ymax = int((y_center + height/2) * img_height)

        obj = ET.SubElement(root, "object")
        ET.SubElement(obj, "name").text = class_list[int(class_id)]
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = "0"
        ET.SubElement(obj, "difficult").text = "0"

        bbox = ET.SubElement(obj, "bndbox")
        ET.SubElement(bbox, "xmin").text = str(max(xmin, 0))
        ET.SubElement(bbox, "ymin").text = str(max(ymin, 0))
        ET.SubElement(bbox, "xmax").text = str(min(xmax, img_width))
        ET.SubElement(bbox, "ymax").text = str(min(ymax, img_height))

    # Create XML file
    tree = ET.ElementTree(root)
    xml_filename = os.path.splitext(os.path.basename(image_file))[0] + '.xml'
    tree.write(os.path.join(output_dir, 'annotations', xml_filename))

def convert_subset(yolo_dir, image_dir, class_list, output_dir):
    # Create output directories
    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'annotations'), exist_ok=True)

    # Process each YOLO annotation file
    for filename in os.listdir(yolo_dir):
        if filename.endswith('.txt'):
            yolo_file = os.path.join(yolo_dir, filename)
            image_file = os.path.join(image_dir, os.path.splitext(filename)[0] + '.png')
            
            if os.path.exists(image_file):
                # Convert annotation
                yolo_to_voc(yolo_file, image_file, class_list, output_dir)
                
                # Copy image to new directory
                shutil.copy2(image_file, os.path.join(output_dir, 'images'))
                
                print(f"Converted and copied {filename}")
            else:
                print(f"Image not found for {filename}")

def convert_dataset(base_dir, class_file, output_base_dir):
    # Read class list
    with open(class_file, 'r') as f:
        class_list = [line.strip() for line in f.readlines()]

    # Process each subset
    for subset in ['train', 'val', 'test']:
        yolo_dir = os.path.join(base_dir, subset, 'labels')
        image_dir = os.path.join(base_dir, subset, 'images')
        output_dir = os.path.join(output_base_dir, subset)

        if os.path.exists(yolo_dir) and os.path.exists(image_dir):
            print(f"Processing {subset} subset...")
            convert_subset(yolo_dir, image_dir, class_list, output_dir)
        else:
            print(f"Skipping {subset} subset: directory not found")

# Usage
base_dir = 'YoloXRaysTeeth'
class_file = 'YoloXRaysTeeth/classes.txt'  # File containing class names, one per line
output_base_dir = 'YoloXRaysTeeth_VOC'

convert_dataset(base_dir, class_file, output_base_dir)