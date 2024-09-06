import os
import xml.etree.ElementTree as ET
from PIL import Image
import shutil
import argparse

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

def voc_to_yolo(xml_file, image_file, class_list, output_dir):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Get image dimensions
    img_width = int(root.find('size/width').text)
    img_height = int(root.find('size/height').text)
    if class_list == None: # find class_list from VOC names
        for obj in root.findall('object'):
            class_name = obj.find('name').text
            if class_name not in class_list:
                class_list.append(class_name)
    #with open(os.path.join(output_dir, 'classes.txt'), 'w') as f:
     #   f.write('\n'.join(class_list))

    # Process each object in the XML
    yolo_lines = []
    for obj in root.findall('object'):
        class_name = obj.find('name').text
        class_id = class_list.index(class_name)

        bbox = obj.find('bndbox')
        xmin = float(bbox.find('xmin').text)
        ymin = float(bbox.find('ymin').text)
        xmax = float(bbox.find('xmax').text)
        ymax = float(bbox.find('ymax').text)

        # Convert to YOLO format
        x_center = (xmin + xmax) / (2 * img_width)
        y_center = (ymin + ymax) / (2 * img_height)
        width = (xmax - xmin) / img_width
        height = (ymax - ymin) / img_height

        yolo_lines.append(f"{class_id} {x_center} {y_center} {width} {height}")

    # Write YOLO file
    yolo_filename = os.path.splitext(os.path.basename(image_file))[0] + '.txt'
    with open(os.path.join(output_dir, 'labels', yolo_filename), 'w') as f:
        f.write('\n'.join(yolo_lines))
    return class_list

def get_classes_from_xml_file(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    class_list = []
    for obj in root.findall('object'):
        class_name = obj.find('name').text
        if class_name not in class_list:
            class_list.append(class_name)
    return class_list
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

    # Process each subset
    for subset in ['train', 'val', 'test']:
        input_dir = os.path.join(base_dir, subset, 'labels' if conversion_type == 'yolo2voc' else 'annotations')
        image_dir = os.path.join(base_dir, subset, 'images')
        output_dir = os.path.join(output_base_dir, subset)

        if os.path.exists(input_dir) and os.path.exists(image_dir):
            print(f"Processing {subset} subset...")
            convert_subset(input_dir, image_dir, class_list, output_dir, conversion_type)
        else:
            print(f"Skipping {subset} subset: directory not found")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert between YOLO and VOC formats.")
    parser.add_argument("-ct", "--conversion_type", choices=['yolo2voc', 'voc2yolo'], help="Conversion direction")
    parser.add_argument("-i","--input", help="Base directory of the dataset")
    parser.add_argument("-c","--class_file", help="File containing class names, one per line")
    parser.add_argument("-o","--output", help="Output base directory")

    args = parser.parse_args()

    convert_dataset(args.input, args.class_file, args.output, args.conversion_type)