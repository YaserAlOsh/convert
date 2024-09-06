import os
import json
import shutil
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict
from PIL import Image
from constants import YOLO,COCO,PASCAL_VOC
# Import conversion functions
from voc_coco_conv import voc_to_coco, coco_to_voc
from yolo_coco_conv import coco_to_yolo, yolo_to_coco
from yolo_voc_conv import yolo_to_voc, voc_to_yolo, get_classes_from_xml_file

class FormatConverter(ABC):
    @abstractmethod
    def convert(self, input_file: str, image_file: str, class_list: List[str], output_dir: str) -> None:
        pass

    @property
    @abstractmethod
    def input_extension(self) -> str:
        pass
    
    @property
    def input_subfolder(self) -> str:
        pass
    
    @property
    @abstractmethod
    def output_subfolder(self) -> str:
        pass
    
    @property
    @abstractmethod
    def one_file_input(self) -> bool:
        pass

    @property
    def input_file(self):
        pass

    @property
    @abstractmethod
    def one_file_output(self) -> bool:
        pass
    
    def get_class_list(self,subset_folder):
        return None

    def save_data(self):
        pass
    def processing_complete(self,out_path,subsets,class_list):
        pass

class YOLOToVOCConverter(FormatConverter):
    def convert(self, input_file: str, image_file: str, class_list: List[str], output_dir: str) -> None:
        yolo_to_voc(input_file, image_file, class_list, output_dir)

    @property
    def input_extension(self) -> str:
        return '.txt'
    @property
    def input_subfolder(self) -> str:
        return 'labels'
    @property
    def output_subfolder(self) -> str:
        return 'annotations'
    @property
    def one_file_input(self) -> bool:
        return False
    
    @property
    def one_file_output(self) -> bool:
        return False

class VOCToYOLOConverter(FormatConverter):
    def convert(self, input_file: str, image_file: str, class_list: List[str], output_dir: str) -> None:
        voc_to_yolo(input_file, image_file, class_list, output_dir)

    @property
    def input_extension(self) -> str:
        return '.xml'
    @property
    def input_subfolder(self) -> str:
        return 'annotations'
    
    @property
    def output_subfolder(self) -> str:
        return 'labels'
    @property
    def one_file_input(self) -> bool:
        return False
    
    @property
    def one_file_output(self) -> bool:
        return False
    
    def get_class_list(self,subset_folder):
        class_list = []
        print('get class list')
        for filename in os.listdir(os.path.join(subset_folder,self.input_subfolder)):
            if not filename.endswith(self.input_extension):
                print(f"Image not found for {filename}")
                continue
            input_file = os.path.join(subset_folder,self.input_subfolder, filename)
            for c in get_classes_from_xml_file(input_file):
                if c not in class_list: class_list.append(c)
            #print(class_list)
        #class_list = np.array(class_list).flatten().tolist()
        #class_list = 
        return class_list
    def processing_complete(self,out_path,subsets,class_list):
        # create dataset.yaml file
        res = ''
        for sb in subsets:
            s,v = sb
            res = f'{res}{s}: {v}\n'
        #if train_path != None:
        #    res = f'{res}train: {train_path}\n'
        #if val_path != None:
        #    res = f'{res}val: {val_path}\n'
        #if test_path != None:
        #    res = f'{res}test: {test_path}\n'
        res = f'{res}nc: {len(class_list)}\n'
        m_class_names = [f'{c}' for c in class_list]
        res = f'{res}names: {m_class_names}'
        print(os.path.join(out_path,'dataset.yaml'),'w')
        with open(os.path.join(out_path,'dataset.yaml'),'w') as f:
            f.write(res)
        with open(os.path.join(out_path,'classes.txt'),'w') as f:
            f.write('\n'.join(class_list))
        return res


class COCOToYOLOConverter(FormatConverter):
    def convert(self, input_file: str, image_file: str, class_list: List[str], output_dir: str) -> None:
        with open(input_file,'r') as f:
            coco_data = json.load(f)
            coco_to_yolo(coco_data, output_dir)

    @property
    def input_extension(self) -> str:
        return '.json'

    @property
    def output_subfolder(self) -> str:
        return 'labels'
    @property
    def one_file_input(self) -> bool:
        return True
    
    @property
    def one_file_output(self) -> bool:
        return False
    @property
    def input_file(self) -> str:
        return 'annotations.json'
    def get_class_list(self,subset_folder):
        class_list = []
        print('get class list')
        with open(os.path.join(subset_folder,self.input_file),'r') as f:
            coco_data = json.load(f)
            class_list = list(map(lambda x: x['name'], coco_data['categories']))
        return class_list
    def processing_complete(self,out_path,subsets,class_list):
        # create dataset.yaml file
        res = ''
        for sb in subsets:
            s,v = sb
            res = f'{res}{s}: {v}\n'
        #if train_path != None:
        #    res = f'{res}train: {train_path}\n'
        #if val_path != None:
        #    res = f'{res}val: {val_path}\n'
        #if test_path != None:
        #    res = f'{res}test: {test_path}\n'
        res = f'{res}nc: {len(class_list)}\n'
        m_class_names = [f'{c}' for c in class_list]
        res = f'{res}names: {m_class_names}'
        print(os.path.join(out_path,'dataset.yaml'),'w')
        with open(os.path.join(out_path,'dataset.yaml'),'w') as f:
            f.write(res)
        with open(os.path.join(out_path,'classes.txt'),'w') as f:
            f.write('\n'.join(class_list))
        return res

class YOLOToCOCOConverter(FormatConverter):
    def convert(self, input_file: str, image_file: str, class_list: List[str], output_dir: str):
        return yolo_to_coco(input_file, image_file, class_list)

    @property
    def input_extension(self) -> str:
        return '.txt'
    @property
    def input_subfolder(self) -> str:
        return 'labels'
    @property
    def output_subfolder(self) -> str:
        return 'annotations'
    @property
    def one_file_input(self) -> bool:
        return False
    
    @property
    def one_file_output(self) -> bool:
        return True
    def save_data(self,data,output_dir) -> None:
        with open(os.path.join(output_dir,'annotations.json'),'w') as f:
            json.dump(data, f, indent=4)

class VOCToCOCOConverter(FormatConverter):
    def convert(self, input_file: str, image_file: str, class_list: List[str], output_dir: str):
        return voc_to_coco(input_file, image_file)

    @property
    def input_extension(self) -> str:
        return '.xml'
    @property
    def input_subfolder(self) -> str:
        return 'annotations'
    @property
    def output_subfolder(self) -> str:
        return 'annotations'
    
    @property
    def one_file_input(self) -> bool:
        return False
    
    @property
    def one_file_output(self) -> bool:
        return True
    def save_data(self,data,output_dir) -> None:
        with open(output_dir,'annotations.json') as f:
            json.dump(data, f, indent=4)

class COCOToVOCConverter(FormatConverter):
    def convert(self, input_file: str, image_file: str, class_list: List[str], output_dir: str) -> None:
        coco_to_voc(input_file, image_file, class_list, output_dir)

    @property
    def input_extension(self) -> str:
        return '.json'

    @property
    def output_subfolder(self) -> str:
        return 'labels'
    @property
    def one_file_input(self) -> bool:
        return True
    
    @property
    def one_file_output(self) -> bool:
        return False
    @property
    def input_file(self) -> str:
        return 'annotations.json'

# Mapping conversion types to their corresponding classes
CONVERTER_CLASSES: Dict[str, FormatConverter] = {
    'yolo2voc': YOLOToVOCConverter,
    'voc2yolo': VOCToYOLOConverter,
    'coco2yolo': COCOToYOLOConverter,
    'yolo2coco': YOLOToCOCOConverter,
    'voc2coco': VOCToCOCOConverter,
    'coco2voc': COCOToVOCConverter
}

def get_conversion_type(input_format,output_format):
    if input_format == YOLO:
        if output_format == COCO:
            return "yolo2coco"
        elif output_format == PASCAL_VOC:
            return "yolo2voc"
    elif input_format == COCO:
        if output_format==YOLO:
            return "coco2yolo"
        elif output_format==PASCAL_VOC:
            return "coco2voc"
    elif input_format == PASCAL_VOC:
        if output_format==YOLO:
            return "voc2yolo"
        elif output_format==COCO:
            return "voc2coco"
    return "not_supported"

def convert_subset(subset_dir: str, class_list: List[str], output_dir: str, converter: FormatConverter) -> None:
    #print(input_dir)
    #print(image_dir)
    
    image_dir = os.path.join(subset_dir,'images')
    # Create output directories
    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, converter.output_subfolder), exist_ok=True)
    accumulate_data = []
    if converter.one_file_input:
        print('one input file')
        input_file = os.path.join(subset_dir, converter.input_file)
        res = converter.convert(input_file, image_dir, class_list, output_dir)
        if converter.one_file_output:
            converter.save_data(res,output_dir)
        #print(image_dir)
        for filename in os.listdir(image_dir):
            #if os.path.exists(image_file):
            #print(os.path.join(image_dir,filename))
            shutil.copy2(os.path.join(image_dir,filename), os.path.join(output_dir, 'images'))
    elif converter.one_file_output:
        #print(input_dir)
        res = converter.convert(os.path.join(subset_dir,converter.input_subfolder), image_dir, class_list, output_dir)
        converter.save_data(res,output_dir)
        for filename in os.listdir(image_dir):
            #if os.path.exists(image_file):
            #print(os.path.join(image_dir,filename))
            shutil.copy2(os.path.join(image_dir,filename), os.path.join(output_dir, 'images'))
    else:
        #print(input_dir)
        #print(image_dir)
        # Process each annotation file
        input_dir = os.path.join(subset_dir,converter.input_subfolder)
        for filename in os.listdir(input_dir):
            if not filename.endswith(converter.input_extension):
                print(f"Image not found for {filename}")
                continue
            input_file = os.path.join(input_dir, filename)
            image_file = os.path.join(image_dir, os.path.splitext(filename)[0] + '.png')
            if not os.path.exists(image_file):
                image_file = os.path.join(image_dir, os.path.splitext(filename)[0] + '.jpeg')
            if os.path.exists(image_file):
                # Convert annotation
                res = converter.convert(input_file, image_file, class_list, output_dir)
                #if converter.one_file_output:
                #    accumulate_data.append(res)
                # Copy image to new directory
                shutil.copy2(image_file, os.path.join(output_dir, 'images'))

                print(f"Converted and copied {filename}")
                    
        #if converter.one_file_output:
         #   converter.save_data(accumulate_data,output_dir)

def convert_dataset(base_dir: str, class_file: str, output_base_dir: str, conversion_type: str) -> None:
    if class_file != None and class_file != 'No file selected':
        # Read class list
        with open(class_file, 'r') as f:
            class_list = [line.strip() for line in f.readlines()]
    else: class_list = None
    # Determine the appropriate converter class
    ConverterClass = CONVERTER_CLASSES.get(conversion_type)
    if ConverterClass is None:
        raise ValueError(f"Unsupported conversion type: {conversion_type}")

    converter = ConverterClass()
    subset_exist = False
    subsets_paths = []
    for subset in ['train', 'val', 'test']:
        subset_dir = os.path.join(base_dir,subset)
        input_dir = os.path.join(base_dir, subset, 'labels' if 'yolo2' in conversion_type else 'annotations')
        image_dir = os.path.join(base_dir, subset, 'images')
        output_dir = os.path.join(output_base_dir, subset)
        print(input_dir)
        print(image_dir)
        if os.path.exists(input_dir) and os.path.exists(image_dir):
            if class_list == None and subset == "train": 
                class_list = converter.get_class_list(subset_dir)
                print(f'classes: {class_list}')
            subset_exist = True
            subsets_paths.append((subset,subset_dir))
            print(f"Processing {subset} subset...")
            convert_subset(subset_dir, class_list, output_dir, converter)
        else:
            print(f"Skipping {subset} subset: directory not found")
    if subset_exist:
        print("Processing Complete...")
        converter.processing_complete(output_base_dir,subsets_paths,class_list)
    if not subset_exist:
        # Convert without subsets
        input_dir = os.path.join(base_dir, 'labels' if 'yolo' in conversion_type else 'annotations')
        image_dir = os.path.join(base_dir, 'images')
        output_dir = os.path.join(output_base_dir, 'full_dataset')
        if os.path.exists(input_dir) and os.path.exists(image_dir):
            if class_list == None: 
                class_list = converter.get_class_list(subset_dir)
            convert_subset(input_dir, image_dir, class_list, output_dir, converter)
            converter.processing_complete(output_base_dir,[],class_list)
