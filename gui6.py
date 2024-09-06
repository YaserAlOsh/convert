import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QFileDialog, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QDir, QThread, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from constants import PASCAL_VOC, YOLO, COCO
import json
from plot_annotations import process_dataset
from cc import convert_dataset, get_conversion_type
from PyQt6.QtGui import QPalette, QColor
from loading_dialog import LoadingDialog
from utils import resource_path

class ConversionThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.function(*self.args, **self.kwargs)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
class ModernDatasetConverterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_file = resource_path("app_settings.json")
        self.last_directory = ""
        self.dark_stylesheet_file = resource_path("dark_style.qss")
        self.light_stylesheet_file = resource_path("light_style.qss")
        self.last_option = "yolo2voc"
        self.initUI()
        self.load_settings()
        self.load_stylesheet()
    def load_stylesheet(self):
        app = QApplication.instance()
        if app.palette().color(QPalette.ColorRole.Window).lightness() < 128:
            stylesheet_file = self.dark_stylesheet_file
        else:
            stylesheet_file = self.light_stylesheet_file

        try:
            with open(stylesheet_file, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Stylesheet file '{stylesheet_file}' not found.")
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Input format selection
        input_layout = self.create_labeled_combobox('Input Format:', [YOLO, COCO, PASCAL_VOC])
        self.input_format = input_layout.itemAt(1).widget()
        layout.addLayout(input_layout)

        # Output format selection
        output_layout = self.create_labeled_combobox('Output Format:', [YOLO, COCO, PASCAL_VOC])
        self.output_format = output_layout.itemAt(1).widget()
        layout.addLayout(output_layout)

        # Input directory selection
        self.input_dir, input_dir_layout = self.create_directory_selection('Input Directory:')
        layout.addLayout(input_dir_layout)

        # Input directory drop area
        self.input_label = self.create_drop_area("Drop here for Input Directory", "input-drop-area")
        layout.addWidget(self.input_label)

        # Class file selection (for YOLO)
        self.class_file, class_file_layout = self.create_file_selection('Class File (for YOLO):')
        layout.addLayout(class_file_layout)

        # Output directory selection
        self.output_dir, output_dir_layout = self.create_directory_selection('Output Directory:')
        layout.addLayout(output_dir_layout)

        # Output directory drop area
        self.output_label = self.create_drop_area("Drop here for Output Directory", "output-drop-area")
        layout.addWidget(self.output_label)
        # Create horizontal layout
        button_layout = QHBoxLayout()
        
        # Annotate button
        self.convert_button = QPushButton('Annotate')
        self.convert_button.clicked.connect(self.annotate)
        self.convert_button.setObjectName("annotate-button")
        button_layout.addWidget(self.convert_button)
        # Convert button
        self.convert_button = QPushButton('Convert')
        self.convert_button.clicked.connect(self.convert)
        self.convert_button.setObjectName("convert-button")
        button_layout.addWidget(self.convert_button)
        # Add horizontal layout to main layout
        layout.addLayout(button_layout)
        
        self.setAcceptDrops(True)
        self.setGeometry(100, 100, 600, 500)
        self.setLayout(layout)
        self.setWindowTitle('Dataset Converter')

    def create_labeled_combobox(self, label_text, items):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        combobox = QComboBox()
        combobox.addItems(items)
        layout.addWidget(label)
        layout.addWidget(combobox)
        return layout

    def create_directory_selection(self, label_text):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        dir_label = QLabel('No directory selected')
        dir_label.setObjectName("directory-label")
        button = QPushButton('Select')
        button.clicked.connect(lambda: self.select_directory(dir_label))
        layout.addWidget(label)
        layout.addWidget(dir_label)
        layout.addWidget(button)
        return dir_label, layout

    def create_file_selection(self, label_text):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        file_label = QLabel('No file selected')
        file_label.setObjectName("file-label")
        button = QPushButton('Select')
        button.clicked.connect(lambda: self.select_file(file_label))
        layout.addWidget(label)
        layout.addWidget(file_label)
        layout.addWidget(button)
        return file_label, layout

    def create_drop_area(self, text, object_name):
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setObjectName(object_name)
        label.setFixedHeight(75)
        return label

    def select_directory(self, label):
        dir_name = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if dir_name:
            label.setText(dir_name)

    def select_file(self, label):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Select File', '', 'Text Files (*.txt)')
        if file_name:
            label.setText(file_name)

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
                mouse_pos = event.position().toPoint()
                if self.input_label.geometry().contains(mouse_pos):
                    self.input_dir.setText(folder_path)
                elif self.output_label.geometry().contains(mouse_pos):
                    self.output_dir.setText(folder_path)

    def convert(self):
        try:
            input_format = self.input_format.currentText()
            output_format = self.output_format.currentText()
            input_dir = self.input_dir.text()
            output_dir = self.output_dir.text()
            class_file = self.class_file.text()

            if input_dir == 'No directory selected' or output_dir == 'No directory selected':
                QMessageBox.warning(self, 'Error', 'Please select input and output directories.')
                return

            if input_format == YOLO:
                if class_file == 'No file selected':
                    class_file = os.path.join(input_dir, "classes.txt")
                    if not os.path.exists(class_file):
                        QMessageBox.warning(self, 'Error', 'Please select a class file for YOLO format.')
                        return

            self.save_settings()
            self.loading_dialog = LoadingDialog(self)
            self.loading_dialog.start_animation()
            self.loading_dialog.show()
            conversion_type = get_conversion_type(input_format, output_format)
            self.annotation_thread = ConversionThread(convert_dataset,
                    input_dir,class_file,output_base_dir=output_dir,conversion_type=conversion_type)
            self.annotation_thread.finished.connect(self.on_conversion_finished)
            self.annotation_thread.error.connect(self.on_conversion_error)
            self.annotation_thread.start()
            #convert_dataset(input_dir, class_file, output_base_dir=output_dir, conversion_type=conversion_type)
            #self.loading_dialog.close()
            #QMessageBox.information(self, 'Success', 'Conversion completed successfully!')
            
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
            self.save_settings()
            self.loading_dialog = LoadingDialog(self)
            self.loading_dialog.start_animation()
            self.loading_dialog.show()
            self.annotation_thread = ConversionThread(process_dataset, input_dir,output_dir,class_file,input_format)
            self.annotation_thread.finished.connect(self.on_annotation_finished)
            self.annotation_thread.error.connect(self.on_annotation_error)
            self.annotation_thread.start()
            #process_dataset(input_dir,output_dir,class_file,input_format)
            #self.loading_dialog.close()
            #QMessageBox.information(self, 'Success', 'Annotation completed successfully!')
            
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

    def get_stylesheet(self):
        return """
        
        """
    def on_conversion_finished(self):
        self.loading_dialog.hide()
        QMessageBox.information(self, 'Success', 'Conversion completed successfully!')

    def on_conversion_error(self, error_message):
        self.loading_dialog.hide()
        QMessageBox.critical(self, 'Error', f'An error occurred during conversion: {error_message}')
    def on_annotation_finished(self):
        self.loading_dialog.hide()
        QMessageBox.information(self, 'Success', 'Annotation completed successfully!')

    def on_annotation_error(self, error_message):
        self.loading_dialog.hide()
        QMessageBox.critical(self, 'Error', f'An error occurred during annotation: {error_message}')
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # Enable High DPI display with PyQt6
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    
    # Set the application to use the system's color scheme
    if hasattr(Qt.ApplicationAttribute, 'AA_UseStyleSheetPropagationInWidgetStyles'):
        app.setAttribute(Qt.ApplicationAttribute.AA_UseStyleSheetPropagationInWidgetStyles, True)
    ex = ModernDatasetConverterGUI()
    ex.show()
    sys.exit(app.exec())