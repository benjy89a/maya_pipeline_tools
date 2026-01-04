# -*- coding: utf-8 -*-
import pymel.core as pm
from PySide2 import QtWidgets, QtCore

class NamingManager(QtWidgets.QDialog):
    def __init__(self):
        super(NamingManager, self).__init__()
        self.setWindowTitle("Simple Naming Manager")
        self.setMinimumWidth(300)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        # Prefix / Suffix
        self.prefix_input = QtWidgets.QLineEdit(placeholderText="Prefix_")
        self.suffix_input = QtWidgets.QLineEdit(placeholderText="_Suffix")
        
        # Search and Replace
        self.search_input = QtWidgets.QLineEdit(placeholderText="Search")
        self.replace_input = QtWidgets.QLineEdit(placeholderText="Replace")
        
        # Rename Button
        self.rename_btn = QtWidgets.QPushButton("Rename Selected Objects")
        self.rename_btn.setStyleSheet("background-color: #444; height: 30px; font-weight: bold;")

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Add Prefix/Suffix Section
        group_pre_suf = QtWidgets.QGroupBox("Add Prefix / Suffix")
        pre_suf_layout = QtWidgets.QHBoxLayout(group_pre_suf)
        pre_suf_layout.addWidget(self.prefix_input)
        pre_suf_layout.addWidget(self.suffix_input)
        main_layout.addWidget(group_pre_suf)
        
        # Search/Replace Section
        group_sr = QtWidgets.QGroupBox("Search and Replace")
        sr_layout = QtWidgets.QHBoxLayout(group_sr)
        sr_layout.addWidget(self.search_input)
        sr_layout.addWidget(self.replace_input)
        main_layout.addWidget(group_sr)
        
        main_layout.addWidget(self.rename_btn)

    def create_connections(self):
        self.rename_btn.clicked.connect(self.do_rename)

    def do_rename(self):
        selection = pm.ls(sl=True)
        if not selection:
            pm.warning("오브젝트를 먼저 선택해주세요!")
            return
            
        prefix = self.prefix_input.text()
        suffix = self.suffix_input.text()
        search = self.search_input.text()
        replace = self.replace_input.text()

        # Undo 한 번에 되도록 설정
        with pm.UndoChunk():
            for obj in selection:
                current_name = obj.nodeName()
                new_name = current_name
                
                # 1. Search and Replace
                if search:
                    new_name = new_name.replace(search, replace)
                
                # 2. Prefix / Suffix
                new_name = f"{prefix}{new_name}{suffix}"
                
                # Rename 실행
                obj.rename(new_name)
                
        print(f"[Naming Manager] {len(selection)}개의 이름을 변경했습니다.")

# 툴 실행 함수
def show_ui():
    global naming_ui
    try:
        naming_ui.close()
        naming_ui.deleteLater()
    except:
        pass
        
    naming_ui = NamingManager()
    naming_ui.show()

if __name__ == "__main__":
    show_ui()