from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
import os
import shutil
from pathlib import Path
from googletrans import Translator
import unicodedata
import stat
import sys

class FileOperation():
    downloads_path = ""
    desktop_path = ""
    files = []
    def __init__(self):
        self.downloads_path = self.get_path_download()
        self.desktop_path = self.get_path_desktop()
        self.files = self.get_files_from_directory(self.downloads_path)

    def has_hidden_attribute(self, filepath):
        return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)

    def translate_folder_name(self, folder_name):
        translator = Translator()
        en_folder_name = translator.translate(folder_name, dest="en")
        return str(en_folder_name.text)

    def get_path_download(self):
        downloads = "Downloads"
        downloads_path = Path.home() / downloads

        if downloads_path.name != downloads:
            downloads_path = Path.home() / self.translate_folder_name(downloads_path.name)
        
        return str(downloads_path)

    def get_files_from_directory(self, directory_path):
        files = os.listdir(directory_path)
        return files

    def get_path_desktop(self):
        desktop = "Desktop"
        desktop_path = Path.home() / desktop

        if desktop_path.name != desktop:
            desktop_path = Path.home() / self.translate_folder_name(desktop_path.name)
        
        return str(desktop_path)

    def safe_decode(self, file_name):
        try:
            return file_name.encode('latin-1', errors='ignore').decode('latin-1')
        except UnicodeEncodeError:
            return ''.join(c for c in file_name if unicodedata.category(c)[0] != 'C')

    def move_files_to_folder_in_desktop(self, files, desktop_path, directory_path):
        print(desktop_path)
        folder_path = desktop_path+"\MoveDownloads"

        if os.path.isdir(folder_path):
            if self.overwriteAlertDialog():
                if self.get_files_from_directory(folder_path) is None:
                    os.rmdir(folder_path)
                else:
                    shutil.rmtree(folder_path)
                self.createFolder(folder_path)
        else:
            self.createFolder(folder_path)
                
        
    def createFolder(self, folder_path):
        try:
            os.mkdir(folder_path)
            self.move_files_to_desktop(self.files, folder_path, self.downloads_path)
            sys.exit()
        except Exception as e:
            print(e)
        
    
    def overwriteAlertDialog(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Warning")
        msg_box.setText("The destination folder already exists. Do you want to overwrite it?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            print("User clicked Yes")
            return True
        else:
            print("User clicked No")
            return False
        
            
    def move_files_to_desktop(self, files, desktop_path, directory_path):
        for file in files:
            decoded_file = self.safe_decode(file)
            if decoded_file is None:
                continue  # Skip problematic files

            print(decoded_file)

            new_path = os.path.join(desktop_path, decoded_file)
            old_path = os.path.join(directory_path, file)

            if not self.has_hidden_attribute(old_path):
                try:
                    shutil.move(old_path, new_path)
                except Exception as e:
                    print(f"Error moving file '{file}': {e}")
            else:
                print(f"File '{file}' has hidden attribute.")
        
        
class MyWindow(QDialog):
    window_width = 400
    label_width = int(window_width-100)
    font_size = 15
    def __init__(self):
        super().__init__()

        # Create labels
        self.moveWithoutFolderLbl = QLabel("Move files to OUTSIDE a folder!")
        self.moveInsideFolderLbl = QLabel("Move files to INSIDE a folder!")

        font = self.font()
        
        font.setPointSize(self.font_size)
        self.moveWithoutFolderLbl.setFont(font)

        font.setPointSize(self.font_size)
        self.moveInsideFolderLbl.setFont(font)

        self.moveWithoutFolderLbl.setStyleSheet("background-color: lightblue;")
        self.moveInsideFolderLbl.setStyleSheet("background-color: lightgreen;")
        self.setStyleSheet("background-color: black;")

        self.moveWithoutFolderLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.moveInsideFolderLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setFixedSize(self.size())

        
        # Set up layout
        layout = QHBoxLayout()
        layout.addWidget(self.moveWithoutFolderLbl, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.moveInsideFolderLbl, alignment=Qt.AlignmentFlag.AlignRight)

        self.moveWithoutFolderLbl.setFixedWidth(self.label_width)
        self.moveInsideFolderLbl.setFixedWidth(self.label_width)

        self.setLayout(layout)

        # Connect click events to custom slots
        self.moveWithoutFolderLbl.mousePressEvent = self.moveWithoutFolderLbl_clicked
        self.moveInsideFolderLbl.mousePressEvent = self.moveInsideFolderLbl_clicked

        self.setWindowTitle('MoveDownloads')

        QApplication.setStyle("Fusion")
        self.show()

    def moveWithoutFolderLbl_clicked(self, event):
        fileOperator = self.getFileOperator()
        fileOperator.move_files_to_desktop(fileOperator.files, fileOperator.desktop_path, fileOperator.downloads_path)
        sys.exit()

    def moveInsideFolderLbl_clicked(self, event):
        fileOperator = self.getFileOperator()
        fileOperator.move_files_to_folder_in_desktop(fileOperator.files, fileOperator.desktop_path, fileOperator.downloads_path)
        
    def getFileOperator(self):
        fileOperator = FileOperation()
        return fileOperator

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
