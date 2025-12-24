from PySide2 import QtWidgets, QtCore, QtGui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.cmds as cmds
from . import scene_validation_tool


class SceneValidatorUI(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SceneValidatorUI, self).__init__(parent=parent)
        self.core = scene_validation_tool.SceneValidatorCore()
        self.setWindowTitle("Advanced Scene Validator")
        self.setMinimumSize(450, 650)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # 1. 씬 클린업 섹션 (전체 씬 대상)
        cleanup_group = QtWidgets.QGroupBox("Scene Cleanup")
        cleanup_layout = QtWidgets.QHBoxLayout(cleanup_group)

        self.btn_del_unknown = QtWidgets.QPushButton("Del Unknown")
        self.btn_fix_uvsets = QtWidgets.QPushButton("Clean UV Sets")
        self.btn_fix_uvsets.setToolTip("map1만 남기고 모든 UV 세트를 정리합니다.")

        cleanup_layout.addWidget(self.btn_del_unknown)
        cleanup_layout.addWidget(self.btn_fix_uvsets)
        layout.addWidget(cleanup_group)

        # 2. 결과 리스트
        self.result_list = QtWidgets.QListWidget()
        self.result_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.result_list)

        # 3. 하단 버튼
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_check = QtWidgets.QPushButton("Run All Checks")
        self.btn_check.setFixedHeight(40)
        self.btn_check.setStyleSheet("background-color: #444; font-weight: bond;")

        self.btn_fix = QtWidgets.QPushButton("Fix Selected")
        self.btn_fix.setFixedHeight(40)
        self.btn_fix.setStyleSheet("background-color: #4e5a4e;")

        btn_layout.addWidget(self.btn_check)
        btn_layout.addWidget(self.btn_fix)
        layout.addLayout(btn_layout)

        self.btn_check.clicked.connect(self.run_full_check)
        self.btn_fix.clicked.connect(self.run_fix_basic)
        self.btn_del_unknown.clicked.connect(self.run_del_unknown)
        self.btn_fix_uvsets.clicked.connect(self.run_fix_basic)


        self.result_list.itemSelectionChanged.connect(self.sync_selection_to_maya)

    def add_selection_header(self, title):
        item = QtWidgets.QListWidgetItem(title)
        item.setFlags(QtCore.Qt.NoItemFlags)
        item.setBackground(QtGui.QColor(50, 50, 50))
        item.setForeground(QtGui.QColor("#FFCF5E"))
        self.result_list.addItem(item)

    def run_full_check(self):
        self.result_list.clear()
        targets = self.core.get_all_mesh_transforms()

        if not targets:
            self.result_list.addItem("검사할 대상(Mesh, Joint)이 없습니다.")
            return

        bad_names = self.core.check_naming_conventions(targets)
        bad_history = self.core.check_history(targets)
        bad_xform = self.core.check_freeze_transforms(targets)

        bad_uvsets = self.core.check_multi_uvsets(targets)
        overlap_faces = self.core.check_uv_overlapping(targets)

        if bad_names:
            self.add_selection_header("--- Naming Issues ---")
            for n in bad_names: self.result_list.addItem(n)

        if bad_history:
            self.add_selection_header("--- Histroy Detected ---")
            for h in bad_history: self.result_list.addItem(h)

        if bad_xform:
            self.add_selection_header("--- Unfrozen Transforms ---")
            for t in bad_xform: self.result_list.addItem(t)

        if bad_uvsets:
            self.add_selection_header("--- UV Set Issues ---")
            for u in bad_uvsets: self.result_list.addItem(u)

        if overlap_faces:
            self.add_selection_header("--- UV Overlap (Faces) ---")
            for f in overlap_faces: self.result_list.addItem(f)

        if self.result_list.count() == 0:
            self.result_list.addItem("모든 검사를 통과했습니다.")

    def sync_selection_to_maya(self):
        selected_items = self.result_list.selectedItems()
        to_select = []

        for item in selected_items:
            text = item.text()

            if text.startswith("---"):
                continue
                clean_name = text.split('(')[0]
                if cmds.objExists(clean_name):
                    to_select.append(clean_name)

        if to_select:
            cmds.select(to_select, replace=True)

    def run_fix_basic(self):
        selected_items = self.result_list.selectedItems()
        nodes = [i.text().split('(')[0] for i in selected_items if not i.text().startswith("---")]

        if not nodes:
            QtWidgets.QMessageBox.warning(self,"알림","수정할 노드를 리스트에서 선택하세요")
            return
        self.core.fix_history_and_transforms(nodes)
        self.run_full_check()

    def run_del_unknown(self):
        removed = self.core.cleanup_unknown_nodes()
        QtWidgets.QMessageBox.information(self, "완료",f"{len(removed)}개의 Unknown 노드를 삭제 했습니다.")

    def run_fix_uvsets(self):
        targets = self.core.get_all_mesh_transforms()
        self.core.cleanup_uvsets(targets)
        self.run_full_check()


def main():
    global validator_window
    try:
        validator_window.close()
        validator_window.deleteLater()
    except:
        pass
    validator_window = SceneValidatorUI()
    validator_window.show(dockable=True)


if __name__ == "__main__":
    main()