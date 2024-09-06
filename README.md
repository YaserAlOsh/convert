## CV-Convert: GUI tool to handle conversion of computer vision object detection datasets formats

Welcome! I built CV-Convert to provide an accessible tool to locally convert your object detection datasets between different formats. This is useful since object detection models usually expect a specific format.

This tool unique features are:
- Simple GUI layout to avoid the hassle of coding or writing commands.
- Runs locally, making it secure and private
- Free
- Open Source

## Supported Formats

Currently, the tool supports conversion between the following formats:

- YOLO (V5 and V8)
- COCO (.json file)
- Pascal VOC (.xml files per annotation)

Please feel free to let me know what other formats you want to see here!

## GUI Layout

![image](https://github.com/user-attachments/assets/3e300240-9bfb-41d6-9141-445a0c6c9337)

The tool supports converting datasets and annotating. Annotation is drawing boxes on images, as per the labels, and saving them as new image files in a new directory.

- **Input Format**: The format of the input dataset.  
- **Output Format [For converting]**: The format to convert the dataset to.  
- **Input Directory**: The directory containing the input dataset. Should contain either (train/test/val) splits or the whole data.  
- Class File [Optional]: A .txt file containing the class names in the dataset, one per line.  
- **Output Directory**: The directory where to store the output. You should create a new directory each time.  

## Command Line Argument

The code also includes a file for command line argument, main.py. Usage is as follows:

```
python main.py --input_format "" --output_format "" --input_dir "" --output_dir "" --class_file ""
input_format: yolo, coco, voc
output_format: yolo, coco, voc
input_dir: The directory containing the input dataset. Should contain either (train/test/val) splits or the whole data.
output_dir: The directory where to store the output. You should create a new directory each time.
class_file: A .txt file containing the class names in the dataset, one per line.
```

### Copyright

Made by Yaser Alosh.
