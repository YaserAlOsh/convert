import json
import os
from PIL import Image
import xml.etree.ElementTree as ET

def yolo_to_coco(yolo_dir, image_dir, class_list):
    coco_data = {
        "images": [],
        "annotations": [],
        "categories": []
    }

    # Create categories
    for i, class_name in enumerate(class_list):
        coco_data["categories"].append({
            "id": i,
            "name": class_name,
            "supercategory": "none"
        })

    annotation_id = 0
    for img_id, filename in enumerate(os.listdir(image_dir)):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(image_dir, filename)
            img = Image.open(img_path)
            width, height = img.size

            coco_data["images"].append({
                "id": img_id,
                "file_name": filename,
                "width": width,
                "height": height
            })

            # Read YOLO annotation
            yolo_file = os.path.join(yolo_dir, os.path.splitext(filename)[0] + '.txt')
            if os.path.exists(yolo_file):
                with open(yolo_file, 'r') as f:
                    for line in f:
                        class_id, x_center, y_center, bbox_width, bbox_height = map(float, line.strip().split())
                        x_center *= width
                        y_center *= height
                        bbox_width *= width
                        bbox_height *= height

                        coco_data["annotations"].append({
                            "id": annotation_id,
                            "image_id": img_id,
                            "category_id": int(class_id),
                            "bbox": [x_center - bbox_width/2, y_center - bbox_height/2, bbox_width, bbox_height],
                            "area": bbox_width * bbox_height,
                            "iscrowd": 0
                        })
                        annotation_id += 1

    return coco_data

def coco_to_yolo(coco_data, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Create a mapping of category_id to index
    category_id_to_index = {cat['id']: i for i, cat in enumerate(coco_data['categories'])}
    # write classes.txt
    class_list = list(map(lambda x: x['name'], coco_data['categories']))
    #with open(os.path.join(output_dir, 'classes.txt'), 'w') as f:
    #    f.write('\n'.join(list(map(lambda x: x['name'], coco_data['categories']))))
    
    for image in coco_data['images']:
        img_id = image['id']
        img_width = image['width']
        img_height = image['height']
        
        yolo_lines = []
        for ann in coco_data['annotations']:
            if ann['image_id'] == img_id:
                cat_index = category_id_to_index[ann['category_id']]
                bbox = ann['bbox']
                x_center = (bbox[0] + bbox[2] / 2) / img_width
                y_center = (bbox[1] + bbox[3] / 2) / img_height
                width = bbox[2] / img_width
                height = bbox[3] / img_height
                
                yolo_lines.append(f"{cat_index} {x_center} {y_center} {width} {height}")
        
        # Write YOLO file
        yolo_filename = os.path.splitext(image['file_name'])[0] + '.txt'
        with open(os.path.join(output_dir,'labels', yolo_filename), 'w') as f:
            f.write('\n'.join(yolo_lines))
    return class_list