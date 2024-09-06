import json
import os
from PIL import Image
import xml.etree.ElementTree as ET
def voc_to_coco(voc_dir, image_dir):
    coco_data = {
        "images": [],
        "annotations": [],
        "categories": []
    }

    categories = set()
    annotation_id = 0

    for img_id, filename in enumerate(os.listdir(voc_dir)):
        if filename.endswith('.xml'):
            xml_path = os.path.join(voc_dir, filename)
            tree = ET.parse(xml_path)
            root = tree.getroot()

            img_filename = root.find('filename').text
            img_path = os.path.join(image_dir, img_filename)
            img = Image.open(img_path)
            width, height = img.size

            coco_data["images"].append({
                "id": img_id,
                "file_name": img_filename,
                "width": width,
                "height": height
            })

            for obj in root.findall('object'):
                category = obj.find('name').text
                categories.add(category)
                bbox = obj.find('bndbox')
                x_min = float(bbox.find('xmin').text)
                y_min = float(bbox.find('ymin').text)
                x_max = float(bbox.find('xmax').text)
                y_max = float(bbox.find('ymax').text)

                coco_data["annotations"].append({
                    "id": annotation_id,
                    "image_id": img_id,
                    "category_id": list(categories).index(category),
                    "bbox": [x_min, y_min, x_max - x_min, y_max - y_min],
                    "area": (x_max - x_min) * (y_max - y_min),
                    "iscrowd": 0
                })
                annotation_id += 1

    # Add categories to COCO data
    for i, category in enumerate(categories):
        coco_data["categories"].append({
            "id": i,
            "name": category,
            "supercategory": "none"
        })

    return coco_data

def coco_to_voc(coco_data, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Create a mapping of category_id to name
    category_id_to_name = {cat['id']: cat['name'] for cat in coco_data['categories']}

    for image in coco_data['images']:
        img_id = image['id']
        img_filename = image['file_name']
        img_width = image['width']
        img_height = image['height']

        root = ET.Element("annotation")
        ET.SubElement(root, "folder").text = "images"
        ET.SubElement(root, "filename").text = img_filename
        
        size = ET.SubElement(root, "size")
        ET.SubElement(size, "width").text = str(img_width)
        ET.SubElement(size, "height").text = str(img_height)
        ET.SubElement(size, "depth").text = "3"

        for ann in coco_data['annotations']:
            if ann['image_id'] == img_id:
                obj = ET.SubElement(root, "object")
                ET.SubElement(obj, "name").text = category_id_to_name[ann['category_id']]
                ET.SubElement(obj, "pose").text = "Unspecified"
                ET.SubElement(obj, "truncated").text = "0"
                ET.SubElement(obj, "difficult").text = "0"

                bbox = ET.SubElement(obj, "bndbox")
                ET.SubElement(bbox, "xmin").text = str(int(ann['bbox'][0]))
                ET.SubElement(bbox, "ymin").text = str(int(ann['bbox'][1]))
                ET.SubElement(bbox, "xmax").text = str(int(ann['bbox'][0] + ann['bbox'][2]))
                ET.SubElement(bbox, "ymax").text = str(int(ann['bbox'][1] + ann['bbox'][3]))

        # Create XML file
        tree = ET.ElementTree(root)
        xml_filename = os.path.splitext(img_filename)[0] + '.xml'
        tree.write(os.path.join(output_dir,'annotations', xml_filename))