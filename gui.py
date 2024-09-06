import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from constants import PASCAL_VOC,YOLO,COCO
import json
from plot_annotations import process_dataset
from cc import convert_dataset,get_conversion_type
# Import the conversion functions here
# from conversion_functions import yolo_to_coco, coco_to_yolo, voc_to_coco, coco_to_voc, yolo_to_voc, voc_to_yolo

class DatasetConverterGUI(QWidget):
    def __init__(self):
        super().__init__()
        # Settings and config
        self.settings_file = "app_settings.json"
        self.last_directory = ""
        self.last_option = "yolo2voc"

        self.initUI()
        self.load_settings()
    def initUI(self):
        layout = QVBoxLayout()

        # Input format selection
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel('Input Format:'))
        self.input_format = QComboBox()
        self.input_format.addItems([YOLO, COCO, PASCAL_VOC])
        input_layout.addWidget(self.input_format)
        layout.addLayout(input_layout)

        # Output format selection
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel('Output Format:'))
        self.output_format = QComboBox()
        self.output_format.addItems([YOLO, COCO, PASCAL_VOC])
        output_layout.addWidget(self.output_format)
        layout.addLayout(output_layout)

        # Input directory selection
        input_dir_layout = QHBoxLayout()
        input_dir_layout.addWidget(QLabel('Input Directory:'))
        self.input_dir = QLabel('No directory selected')
        input_dir_layout.addWidget(self.input_dir)

        self.input_dir_button = QPushButton('Select')
        self.input_dir_button.clicked.connect(self.select_input_dir)
        input_dir_layout.addWidget(self.input_dir_button)
        layout.addLayout(input_dir_layout)
        # Label for input directory drop area
        self.input_label = QLabel("Drop here for Input Directory")
        self.input_label.setStyleSheet("background-color: lightblue; border: 2px solid black;")
        self.input_label.setFixedHeight(75)
        layout.addWidget(self.input_label)

        #Class file selection (for YOLO)
        class_file_layout = QHBoxLayout()
        class_file_layout.addWidget(QLabel('Class File (for YOLO):'))
        self.class_file = QLabel('No file selected')
        class_file_layout.addWidget(self.class_file)
        self.class_file_button = QPushButton('Select')
        self.class_file_button.clicked.connect(self.select_class_file)
        class_file_layout.addWidget(self.class_file_button)
        layout.addLayout(class_file_layout)

        # Output directory selection
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(QLabel('Output Directory:'))
        self.output_dir = QLabel('No directory selected')
        output_dir_layout.addWidget(self.output_dir)
        self.output_dir_button = QPushButton('Select')
        self.output_dir_button.clicked.connect(self.select_output_dir)
        output_dir_layout.addWidget(self.output_dir_button)
        layout.addLayout(output_dir_layout)
        # Label for output directory drop area
        self.output_label = QLabel("Drop here for Output Directory")
        self.output_label.setStyleSheet("background-color: lightgreen; border: 2px solid black;")
        self.output_label.setFixedHeight(75)
        layout.addWidget(self.output_label)
        

        # Convert button
        self.convert_button = QPushButton('Convert')
        self.convert_button.clicked.connect(self.convert)
        layout.addWidget(self.convert_button)

        # Set up drag-and-drop
        self.setAcceptDrops(True)
        self.input_label.setAcceptDrops(True)
        self.output_label.setAcceptDrops(True)
        self.setGeometry(100, 100, 600, 400)  # Set width to 600 and height to 400

        self.setLayout(layout)
        self.setWindowTitle('Dataset Converter')
        self.show()
    
    def select_input_dir(self):
        dir_name = QFileDialog.getExistingDirectory(self, 'Select Input Directory')
        if dir_name:
            self.input_dir.setText(dir_name)

    def select_output_dir(self):
        dir_name = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if dir_name:
            self.output_dir.setText(dir_name)

    def select_class_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Select Class File', '', 'Text Files (*.txt)')
        if file_name:
            self.class_file.setText(file_name)
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            folder_path = urls[0].toLocalFile()
            if QDir(folder_path).exists():
                # Determine which area the folder was dropped onto
                mouse_pos = event.pos()
                if self.input_label.geometry().contains(mouse_pos):
                    #self.last_input_dir = folder_path
                    self.input_dir.setText(folder_path)
                    print(f"Input directory set to: {folder_path}")
                elif self.output_label.geometry().contains(mouse_pos):
                    #self.last_output_dir = folder_path
                    self.output_dir.setText(folder_path)
                    print(f"Output directory set to: {folder_path}")

    def convert(self):
        try:
            input_format = self.input_format.currentText()
            output_format = self.output_format.currentText()
            input_dir = self.input_dir.text()
            output_dir = self.output_dir.text()
            class_file = 'No file selected'
            if input_dir == 'No directory selected' or output_dir == 'No directory selected':
                QMessageBox.warning(self, 'Error', 'Please select input and output directories.')
                return
            # try to get class file
            if input_format == YOLO and class_file== 'No file selected' \
                and os.path.exists(os.path.join(input_dir,"classes.txt")):
                class_file = os.path.join(input_dir,"classes.txt")
            if input_format == YOLO and class_file == 'No file selected':
                QMessageBox.warning(self, 'Error', 'Please select a class file for YOLO format.')
                return
            self.save_settings()
            conversion_type = get_conversion_type(input_format,output_format)
            print(input_dir,class_file,output_dir,conversion_type)
            convert_dataset(input_dir, class_file,output_base_dir=output_dir,conversion_type=conversion_type)
            QMessageBox.information(self, 'Success', 'Conversion completed successfully!')
            
        except Exception as e:
            self.show_error(str(e))
    def annotate(self):
        try:
            input_format = self.input_format.currentText()
            input_dir = self.input_dir.text()
            output_dir = self.output_dir.text()
            class_file = 'No file selected'
            if input_dir == 'No directory selected' or output_dir == 'No directory selected':
                QMessageBox.warning(self, 'Error', 'Please select input and output directories.')
                return
            # try to get class file
            if input_format == YOLO and class_file== 'No file selected' \
                and os.path.exists(os.path.join(input_dir,"classes.txt")):
                class_file = os.path.join(input_dir,"classes.txt")
            if input_format == YOLO and class_file == 'No file selected':
                QMessageBox.warning(self, 'Error', 'Please select a class file for YOLO format.')
                return
            process_dataset(input_dir,output_dir,class_file,input_format)
            QMessageBox.information(self, 'Success', 'Conversion completed successfully!')
            self.save_settings()
        except Exception as e:
            self.show_error(str(e))
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
    def save_settings(self):
        settings = {
            'input_format': self.input_format.currentText(),
            'output_format': self.output_format.currentText(),
            'last_input_dir': self.input_dir.text(),
            'last_output_dir': self.output_dir.text()
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.input_format.setCurrentText(settings.get('input_format', 'yolo'))
                self.output_format.setCurrentText(settings.get('output_format', 'voc'))
                self.input_dir.setText(settings.get('last_input_dir', ''))
                self.output_dir.setText(settings.get('last_output_dir', ''))
                #self.class_file = settings.get('class_file', 'classes.txt') 
                #self.input_format.setText(self.input_format)
                #self.output_format.setText(self.output_format)
                print(f"Loaded settings: {settings}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DatasetConverterGUI()
    sys.exit(app.exec_())