import os
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
from constants import PASCAL_VOC, YOLO, COCO
import xml.etree.ElementTree as ET
from typing import List, Tuple

from abc import ABC, abstractmethod
from typing import List

from abc import ABC, abstractmethod
from typing import List, Tuple,Type
import json
import colorsys
import hashlib
import random


def generate_improved_distinct_colors(n):
    colors = []
    hue = random.random()  # Start with a random hue
    
    for i in range(n):
        saturation = random.uniform(0.5, 1.0)  # Vary saturation
        value = random.uniform(0.7, 1.0)  # Vary brightness (value)
        
        # Convert HSV to RGB
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        
        # Scale to 0-255 range
        color = tuple(int(x * 255) for x in rgb)
        colors.append(color)
        
        # Large hue shift for next color
        hue += random.uniform(0.2, 0.5)
        hue %= 1.0  # Keep hue within 0-1 range
    
    return colors

# Generate 100 distinct colors
NUM_COLORS = 100
COLORS = generate_improved_distinct_colors(NUM_COLORS)
#print(COLORS)
def hash_class_name(class_name):
    return int(hashlib.md5(class_name.encode('utf-8')).hexdigest(), 16)

def get_color_for_class(class_name):
    hash_value = hash_class_name(class_name)
    color_index = hash_value % NUM_COLORS
    return COLORS[color_index]

def draw_boxes_voc(image_path, xml_path, output_path, class_list):
    # Open image
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Parse XML
    tree = ET.parse(xml_path)
    root = tree.getroot()

    colors = ['red', 'green', 'blue', 'yellow', 'purple', 'cyan', 'magenta', 'orange']

    # Draw bounding boxes
    for obj in root.findall('object'):
        name = obj.find('name').text
        class_id = class_list.index(name)
        color = colors[class_id % len(colors)]  # Cycle through colors if there are more classes than colors
        
        bbox = obj.find('bndbox')
        xmin = int(bbox.find('xmin').text)
        ymin = int(bbox.find('ymin').text)
        xmax = int(bbox.find('xmax').text)
        ymax = int(bbox.find('ymax').text)

        # Draw rectangle
        draw.rectangle([xmin, ymin, xmax, ymax], outline=color, width=4)

        # Draw label
        font = ImageFont.load_default(30)
        draw.text((xmin, ymin+20), name, fill=color, font=font)

    # Save image
    img.save(output_path)

def draw_boxes(image_path, annotations, output_path,class_list):
    # Open image
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Draw bounding boxes
    for ant in annotations:
        name, xmin, ymin, xmax, ymax = ant
        if class_list != None:
            class_id = class_list.index(name)
            color = COLORS[class_id % len(COLORS)]  # Cycle through colors if there are more classes than colors
            #print(color)
        else:
            color = get_color_for_class(name)
        # Draw rectangle
        draw.rectangle([xmin, ymin, xmax, ymax], outline=color, width=4)
        # Draw label
        font = ImageFont.load_default(30)
        draw.text((xmin, ymin+20), name, fill=color, font=font)

    # Save image
    img.save(output_path)

class AnnotationFormat(ABC):
    def __init__(self):
        self.x=0
        #self.annotation_folder = 'annotations'
    @abstractmethod
    def parse_annotations(self, annotation_path: str, image_path: str, class_list: List[str]) -> List[Tuple[int, int, int, int, int]]:
        pass

    @property
    @abstractmethod
    def annotation_ext(self) -> str:
        pass
    @property
    @abstractmethod
    def annotation_folder(self):
        pass
    #@abstractmethod
    #def _get_annotation_folder(self):
    #    return 'annotations'
    #@property
    #def annotation_folder(self) -> str:
    #    return 'annotations'
    def process(self,input_dir,class_list,output_dir):
        input_image_dir  = os.path.join(input_dir,'images')
        #print(input_image_dir)
        input_anno_dir   = os.path.join(input_dir,self.annotation_folder)
        #print(input_anno_dir)
        for filename in os.listdir(input_image_dir):
            if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg'):
                image_path = os.path.join(input_image_dir, filename)
                annotation_path = os.path.join(input_anno_dir, os.path.splitext(filename)[0] +\
                                                self.annotation_ext)
                output_path = os.path.join(output_dir, filename)
                #print(annotation_path)
                if os.path.exists(annotation_path):
                    annotation_data = self.parse_annotations(annotation_path, image_path, class_list)
                    draw_boxes(image_path, annotation_data, output_path, class_list)
                    #print(f"Processed {filename}")
                else:
                    print(f"Annotation not found for {filename}")

class VOCFormat(AnnotationFormat):
    def __init__(self):
        super().__init__()
        self._annotation_folder = 'annotations'
     
    def parse_annotations(self, annotation_path: str, image_path: str, class_list: List[str]) -> List[Tuple[int, int, int, int, int]]:
        tree = ET.parse(annotation_path)
        root = tree.getroot()
        annotations = []

        for obj in root.findall('object'):
            name = obj.find('name').text
            #class_id = class_list.index(name)
            bbox = obj.find('bndbox')
            xmin = int(bbox.find('xmin').text)
            ymin = int(bbox.find('ymin').text)
            xmax = int(bbox.find('xmax').text)
            ymax = int(bbox.find('ymax').text)
            annotations.append((name, xmin, ymin, xmax, ymax))
        return annotations

    @property
    def annotation_ext(self) -> str:
        return '.xml'
    @property
    def annotation_folder(self):
        return self._annotation_folder
    #def _get_annotation_folder(self):
    #    return 'annotations'
        
class YOLOFormat(AnnotationFormat):
    def __init__(self):
        super().__init__()
        self._annotation_folder = 'labels'
        pass
    def parse_annotations(self, annotation_path: str, image_path: str, class_list: List[str]) -> List[Tuple[int, int, int, int, int]]:
        # Get image dimensions
        with Image.open(image_path) as img:
            width, height = img.size
        
        annotations = []
        with open(annotation_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                class_id = int(parts[0])
                name = class_list[class_id]
                x_center = float(parts[1]) * width
                y_center = float(parts[2]) * height
                w = float(parts[3]) * width
                h = float(parts[4]) * height
                
                # Convert YOLO format (x_center, y_center, w, h) to (xmin, ymin, xmax, ymax)
                xmin = int(x_center - w / 2)
                ymin = int(y_center - h / 2)
                xmax = int(x_center + w / 2)
                ymax = int(y_center + h / 2)
                
                annotations.append((name, xmin, ymin, xmax, ymax))
        return annotations

    @property
    def annotation_ext(self) -> str:
        return '.txt'
    @property
    def annotation_folder(self):
        return self._annotation_folder
    
class COCOFormat(AnnotationFormat):
    def __init__(self):
        super().__init__()
        self._annotation_folder = 'annotations'
    
    def parse_annotations(self, annotation_path: str, image_path: str, class_list: List[str]) -> List[Tuple[int, int, int, int, int]]:
        with open(annotation_path, 'r') as file:
            data = json.load(file)
        
        annotations = []
        for ann in data['annotations']:
            class_id = ann['category_id'] - 1  # COCO IDs start from 1
            xmin, ymin, width, height = ann['bbox']
            xmax = xmin + width
            ymax = ymin + height
            annotations.append((class_id, xmin, ymin, xmax, ymax))
        return annotations

    @property
    def annotation_ext(self) -> str:
        return '.json'
    @property
    def annotation_folder(self):
        return self._annotation_folder
    def process(self,input_dir,class_list,output_dir):
        #print('COCO process')
        input_anno_dir = os.path.join(input_dir,"annotations.json")
        input_img_dir = os.path.join(input_dir,"images")
        with open(input_anno_dir, 'r') as file:
            coco_data = json.load(file)
        #print('COCO Loaded')
        category_id_to_name = {cat['id']: cat['name'] for i, cat in enumerate(coco_data['categories'])}
        for image in coco_data['images']:
            img_id = image['id']
            img_width = image['width']
            img_height = image['height']
            annts = []
            for ann in coco_data['annotations']:
                if ann['image_id'] == img_id:
                    bbox = ann['bbox']
                    name = category_id_to_name[ann['category_id']]
                    xmin, ymin = bbox[0],bbox[1]
                    xmax, ymax = xmin + bbox[2], ymin + bbox[3]
                    annts.append((name,xmin,ymin,xmax,ymax))
            file_name = image["file_name"]
            #print(file_name)
            output_path = os.path.join(output_dir,file_name)
            if os.path.exists(os.path.join(input_img_dir,file_name)):
                draw_boxes(os.path.join(input_img_dir,file_name),annts,output_path,None)
                #print(f"Processed {file_name}")
            else:
                print(f"Annotation not found for {os.path.join(input_img_dir,file_name)}")
                    
def get_format_class(format_name: str) -> Type[AnnotationFormat]:
    format_classes = {
        PASCAL_VOC.lower(): VOCFormat,
        YOLO.lower(): YOLOFormat,
        COCO.lower(): COCOFormat
    }
    
    if format_name.lower() not in format_classes:
        raise ValueError(f"Unsupported format: {format_name}. Supported formats are: {', '.join(format_classes.keys())}")
    
    return format_classes[format_name.lower()]

def process_dataset(base_dir: str, output_base_dir: str, class_file: str, format_name: str):
    # Get the format class from the format name
    format_class = get_format_class(format_name)
    class_list = None
    format_instance = format_class()
    if class_file != None and os.path.exists(class_file): 
        with open(class_file, 'r') as f:
            class_list = [line.strip() for line in f.readlines()]

    for subset in ['train', 'val', 'test']:
        input_image_dir = os.path.join(base_dir, subset, 'images')
        #format_class = YOLOFormat()
        #print(format_instance.annotation_folder)
        input_anno_dir = os.path.join(base_dir, subset, format_instance.annotation_folder)
        output_dir = os.path.join(output_base_dir, subset)

        if os.path.exists(input_image_dir):
            print(f"Processing {subset} subset...")
            os.makedirs(output_dir, exist_ok=True)
            format_instance.process(os.path.join(base_dir,subset), class_list, output_dir)
            # for filename in os.listdir(input_image_dir):
            #     if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg'):
            #         image_path = os.path.join(input_image_dir, filename)
            #         annotation_path = os.path.join(input_anno_dir, os.path.splitext(filename)[0] + format_instance.annotation_ext)
            #         output_path = os.path.join(output_dir, filename)

            #         if os.path.exists(annotation_path):
            #             annotation_data = format_instance.parse_annotations(annotation_path, image_path, class_list)
            #             draw_boxes(image_path, annotation_data, output_path, class_list)
            #             print(f"Processed {filename}")
            #         else:
            #             print(f"Annotation not found for {filename}")
        else:
            print(f"Skipping {subset} subset: directory not found")

# def process_dataset(base_dir, output_base_dir, class_file):
#     # Read class list
#     with open(class_file, 'r') as f:
#         class_list = [line.strip() for line in f.readlines()]

#     # Process each subset
#     for subset in ['train', 'val', 'test']:
#         input_image_dir = os.path.join(base_dir, subset, 'images')
#         input_anno_dir = os.path.join(base_dir, subset, 'annotations')
#         output_dir = os.path.join(output_base_dir, subset)

#         if os.path.exists(input_image_dir) and os.path.exists(input_anno_dir):
#             print(f"Processing {subset} subset...")
#             os.makedirs(output_dir, exist_ok=True)

#             for filename in os.listdir(input_image_dir):
#                 if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg'):
#                     image_path = os.path.join(input_image_dir, filename)
#                     xml_path = os.path.join(input_anno_dir, os.path.splitext(filename)[0] + '.xml')
#                     output_path = os.path.join(output_dir, filename)

#                     if os.path.exists(xml_path):
#                         draw_boxes(image_path, xml_path, output_path, class_list)
#                         print(f"Processed {filename}")
#                     else:
#                         print(f"Annotation not found for {filename}")
#         else:
#             print(f"Skipping {subset} subset: directory not found")
# # Usage
# base_dir = 'dataset_VOC'  # Your VOC format dataset directory
# output_base_dir = 'dataset_VOC_with_boxes'  # Where to save images with drawn boxes
# class_file = 'YoloXRaysTeeth/classes.txt'  # File containing class names, one per line

# #process_dataset(base_dir, output_base_dir, class_file)
# from argparse import ArgumentParser

# parser = ArgumentParser()
# parser.add_argument("-d","--dir",help="VOC Format Dataset Directory")
# parser.add_argument("-c","--classes",help="File containing class names, one per line")
# parser.add_argument("-o","--output",help="Where to save images with drawn boxes")


# if __name__ == "__main__":
#     # load args
#     args = parser.parse_args()
#     base_dir = args.dir
#     output_base_dir = args.output
#     class_file = args.classes

# process_dataset('D:\Projects\ML\XRaysTeeth\Balanced dataset YOLO - Copy',
#                  'D:\Projects\ML\XRaysTeeth\Balanced dataset annotated',
#                  'D:\Projects\ML\XRaysTeeth\Balanced dataset YOLO - Copy\classes.txt',
#                  'yolo')