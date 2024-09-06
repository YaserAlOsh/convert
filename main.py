import argparse
import os
from cc import convert_dataset, get_conversion_type
# Import the conversion functions here
# from conversion_functions import yolo_to_coco, coco_to_yolo, voc_to_coco, coco_to_voc, yolo_to_voc, voc_to_yolo

def main():
    parser = argparse.ArgumentParser(description="Convert between YOLO, COCO, and Pascal VOC formats.")
    parser.add_argument("-i", "--input_format", choices=['yolo', 'coco', 'voc'], required=True, help="Input format")
    parser.add_argument("-o", "--output_format", choices=['yolo', 'coco', 'voc'], required=True, help="Output format")
    parser.add_argument("-id", "--input_dir", required=True, help="Input directory")
    parser.add_argument("-od", "--output_dir", required=True, help="Output directory")
    parser.add_argument("-c", "--class_file", default='No file selected',required=False, help="Class file for YOLO format")

    args = parser.parse_args()

    if args.input_format == 'yolo' and not args.class_file:
        parser.error("Class file is required for YOLO input format")

    if not os.path.exists(args.input_dir):
        parser.error(f"Input directory does not exist: {args.input_dir}")

    os.makedirs(args.output_dir, exist_ok=True)

    # Perform the conversion here
    # You'll need to implement the logic to call the appropriate conversion function(s)
    # based on the input and output formats
    input_format =args.input_format
    output_format = args.output_format
    input_dir = args.input_dir
    output_dir = args.output_dir
    class_file = args.class_file #'No file selected'

    if input_dir == 'No directory selected' or output_dir == 'No directory selected':
        print('Error', 'Please select input and output directories.')
        return
    # try to get class file
    if input_format == 'YOLO' and class_file== 'No file selected' \
        and os.path.exists(os.path.join(input_dir,"classes.txt")):
        class_file = os.path.join(input_dir,"classes.txt")
    if input_format == 'YOLO' and class_file == 'No file selected':
        print('Error', 'Please select a class file for YOLO format.')
        return
    # Perform conversion
    conversion_type = get_conversion_type(input_format,output_format)
    print(input_dir,class_file,output_dir,conversion_type)
    convert_dataset(input_dir, class_file,output_base_dir=output_dir,conversion_type=conversion_type)
    print('Success', 'Conversion completed successfully!')

if __name__ == "__main__":
    main()