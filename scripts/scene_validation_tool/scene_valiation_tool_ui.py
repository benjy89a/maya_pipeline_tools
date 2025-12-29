# -*- coding: utf-8 -*- 

from PySide2 import QtWidgets, QtCore, QtGui # PySide2 UI 모듈 임포트
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin # Maya 도킹 가능한 위젯 믹스인 임포트
import maya.cmds as cmds # Maya 커맨드 모듈 임포트
from . import scene_validation_tool # 씬 검사 로직 코어 모듈 임포트


class SceneValidatorUI(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    """
    씬의 문제점을 검사하고 수정하는 사용자 인터페이스(UI)를 생성하고 관리하는 클래스입니다.
    이 클래스는 씬의 네이밍 규칙, 히스토리, 트랜스폼, UV 등 다양한 항목을 검사하고,
    결과를 목록으로 보여주며, 선택된 문제나 전체 문제를 수정하는 기능을 제공합니다.
    """
    def __init__(self, parent=None):
        """
        UI 클래스의 생성자입니다.
        창 설정, 코어 로직 초기화, 수정 기능 맵핑, UI 구성을 담당합니다.
        """
        super().__init__(parent=parent) # 부모 클래스의 생성자를 호출합니다.
        self.core = scene_validation_tool.SceneValidatorCore() # 검사 로직을 담고 있는 코어 클래스를 인스턴스화합니다.
        self.setWindowTitle("Advanced Scene Validator") # 윈도우의 제목을 설정합니다.
        self.setMinimumSize(800, 650) # 윈도우의 최소 크기를 설정합니다. (너비 확장)
        self.fix_map = { # 수정 가능한 항목의 헤더와 해당 수정 함수를 맵핑합니다.
            "--- Naming Issues ---": self.core.fix_naming_conventions, # 이름 규칙 위반 문제를 수정하는 함수를 맵핑합니다.
            "--- Histroy Detected ---": self.core.fix_history_and_transforms, # 히스토리 문제를 수정하는 함수를 맵핑합니다.
            "--- Unfrozen Transforms ---": self.core.fix_history_and_transforms, # 동결되지 않은 트랜스폼 문제를 수정하는 함수를 맵핑합니다.
            "--- UV Set Issues ---": self.core.cleanup_uvsets # UV 세트 문제를 수정하는 함수를 맵핑합니다.
        }
        self.setup_ui() # UI를 설정하는 메소드를 호출합니다.

    def setup_ui(self):
        """
        UI의 레이아웃과 위젯들을 생성하고 배치합니다.
        버튼, 리스트 위젯 등을 설정하고 시그널과 슬롯을 연결합니다.
        """
        layout = QtWidgets.QVBoxLayout(self) # 메인 수직 레이아웃을 생성합니다.
        layout.setContentsMargins(10, 10, 10, 10) # 레이아웃의 외부 여백을 설정합니다.
        layout.setSpacing(8) # 레이아웃 내 위젯 간의 간격을 설정합니다.

        # 1. 상단 동작 버튼 (씬 검사)
        top_btn_layout = QtWidgets.QHBoxLayout() # 상단 버튼들을 위한 수평 레이아웃을 생성합니다.
        self.btn_check = QtWidgets.QPushButton("Validate Scene") # '씬 검사' 버튼을 생성합니다.
        self.btn_check.setFixedHeight(40) # 버튼의 높이를 40px로 고정합니다.
        self.btn_check.setStyleSheet("""
            QPushButton { background-color: #5A98D1; color: white; font-weight: bold; border-radius: 5px; }
            QPushButton:hover { background-color: #6BADF5; }
        """) # 버튼의 스타일시트를 설정합니다.
        top_btn_layout.addWidget(self.btn_check) # 버튼을 상단 레이아웃에 추가합니다.
        layout.addLayout(top_btn_layout) # 상단 버튼 레이아웃을 메인 레이아웃에 추가합니다.

        # 2. 결과 및 로그 표시를 위한 스플리터
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal) # 수평 스플리터를 생성합니다.

        # 2-1. 왼쪽: 문제가 발견된 항목 리스트
        result_group = QtWidgets.QGroupBox("문제가 발견된 항목 (Failed Items)") # 그룹박스를 생성합니다.
        result_layout = QtWidgets.QVBoxLayout(result_group) # 그룹박스용 레이아웃을 생성합니다.
        self.result_list = QtWidgets.QListWidget() # 결과를 표시할 리스트 위젯을 생성합니다.
        self.result_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection) # 여러 항목을 선택할 수 있도록 설정합니다.
        self.result_list.setStyleSheet("""
            QListWidget { border: 1px solid #333; border-radius: 5px; background-color: #2D2D2D; }
            QListWidget::item:selected { background-color: #5A98D1; color: white; }
        """) # 리스트 위젯의 스타일시트를 설정합니다.
        result_layout.addWidget(self.result_list) # 리스트 위젯을 그룹 레이아웃에 추가합니다.

        # 2-2. 오른쪽: 검사 진행 내역 로그
        log_group = QtWidgets.QGroupBox("검사 진행 내역 (Validation Log)") # 그룹박스를 생성합니다.
        log_layout = QtWidgets.QVBoxLayout(log_group) # 그룹박스용 레이아웃을 생성합니다.
        self.log_list = QtWidgets.QListWidget() # 로그를 표시할 리스트 위젯을 생성합니다.
        self.log_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection) # 로그는 선택 불가능하도록 설정합니다.
        self.log_list.setStyleSheet("QListWidget { border: 1px solid #333; border-radius: 5px; background-color: #2D2D2D; }") # 스타일시트를 설정합니다.
        log_layout.addWidget(self.log_list) # 로그 리스트를 그룹 레이아웃에 추가합니다.

        splitter.addWidget(result_group) # 스플리터에 문제 항목 그룹을 추가합니다.
        splitter.addWidget(log_group) # 스플리터에 검사 내역 그룹을 추가합니다.
        splitter.setSizes([500, 250]) # 스플리터의 초기 창 크기 비율을 설정합니다.

        layout.addWidget(splitter) # 메인 레이아웃에 스플리터를 추가합니다.

        # 3. 하단 수정 버튼
        bottom_btn_layout = QtWidgets.QHBoxLayout() # 하단 버튼들을 위한 수평 레이아웃을 생성합니다.
        self.btn_fix_selected = QtWidgets.QPushButton("Fix Selected") # '선택 항목 수정' 버튼을 생성합니다.
        self.btn_fix_selected.setFixedHeight(40) # 버튼의 높이를 40px로 고정합니다.
        self.btn_fix_selected.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; border-radius: 5px; }
            QPushButton:hover { background-color: #5CB85C; }
        """) # 버튼의 스타일시트를 설정합니다.

        self.btn_fix_all = QtWidgets.QPushButton("Fix All Fixable") # '전체 수정' 버튼을 생성합니다.
        self.btn_fix_all.setFixedHeight(40) # 버튼의 높이를 40px로 고정합니다.
        self.btn_fix_all.setStyleSheet("""
            QPushButton { background-color: #E67E22; color: white; border-radius: 5px; }
            QPushButton:hover { background-color: #F39C12; }
        """) # 버튼의 스타일시트를 설정합니다.

        bottom_btn_layout.addWidget(self.btn_fix_selected) # 버튼을 하단 레이아웃에 추가합니다.
        bottom_btn_layout.addWidget(self.btn_fix_all) # 버튼을 하단 레이아웃에 추가합니다.
        layout.addLayout(bottom_btn_layout) # 하단 버튼 레이아웃을 메인 레이아웃에 추가합니다.

        # 시그널-슬롯 연결
        self.btn_check.clicked.connect(self.run_full_check) # '씬 검사' 버튼 클릭 시 run_full_check 함수를 실행합니다.
        self.btn_fix_selected.clicked.connect(self.run_fix_selected) # '선택 항목 수정' 버튼 클릭 시 run_fix_selected 함수를 실행합니다.
        self.btn_fix_all.clicked.connect(self.run_fix_all) # '전체 수정' 버튼 클릭 시 run_fix_all 함수를 실행합니다.
        self.result_list.itemSelectionChanged.connect(self.sync_selection_to_maya) # 리스트의 선택이 변경되면 Maya 씬의 선택과 동기화합니다.

    def add_selection_header(self, title):
        """
        '문제가 발견된 항목' 리스트에 카테고리 헤더 아이템을 추가합니다.
        :param title: 헤더로 표시될 문자열
        """
        item = QtWidgets.QListWidgetItem(title) # 리스트 위젯 아이템을 생성합니다.
        item.setFlags(QtCore.Qt.NoItemFlags) # 선택이나 다른 상호작용이 불가능하도록 플래그를 설정합니다.
        item.setBackground(QtGui.QColor(50, 50, 50)) # 배경색을 설정합니다.
        item.setForeground(QtGui.QColor("#FFCF5E")) # 글자색을 설정합니다.
        self.result_list.addItem(item) # 리스트에 아이템을 추가합니다.

    def add_log_entry(self, text, passed):
        """
        '검사 진행 내역' 리스트에 로그를 추가하고, 결과에 따라 색상을 지정합니다.
        :param text: 로그로 표시될 문자열
        :param passed: 검사 통과 여부 (True/False)
        """
        item = QtWidgets.QListWidgetItem(text) # 리스트 위젯 아이템을 생성합니다.
        if passed: # 검사를 통과했다면
            item.setForeground(QtGui.QColor("#4CAF50")) # 초록색으로 표시합니다.
        else: # 검사를 실패했다면
            item.setForeground(QtGui.QColor("#F44336")) # 빨간색으로 표시합니다.
        self.log_list.addItem(item) # 로그 리스트에 아이템을 추가합니다.

    def run_full_check(self):
        """
        씬의 모든 항목에 대한 검사를 수행하고, 문제 항목 리스트와 검사 내역 로그를 모두 업데이트합니다.
        """
        self.result_list.clear() # 이전 문제 항목 결과를 리스트에서 삭제합니다.
        self.log_list.clear() # 이전 검사 내역 로그를 리스트에서 삭제합니다.

        # 1. 알 수 없는 노드(Unknown Node) 검사
        unknown_nodes = cmds.ls(type='unknown') # 씬에서 'unknown' 타입의 모든 노드를 찾습니다.
        if unknown_nodes: # 알 수 없는 노드가 존재하면
            self.add_log_entry(f"• 알 수 없는 노드 검사... 실패 ({len(unknown_nodes)}개)", passed=False) # 로그에 실패로 기록합니다.
            self.add_selection_header("--- Unknown Nodes ---") # 문제 항목 리스트에 헤더를 추가합니다.
            for node in unknown_nodes: # 각 노드에 대해
                self.result_list.addItem(node) # 문제 항목 리스트에 추가합니다.
        else: # 알 수 없는 노드가 없으면
            self.add_log_entry("• 알 수 없는 노드 검사... 통과", passed=True) # 로그에 통과로 기록합니다.

        # 2. 메시(Mesh) 관련 검사
        targets = self.core.get_all_mesh_transforms() # 씬에 있는 모든 메시의 트랜스폼 노드를 가져옵니다.
        if not targets: # 검사할 메시가 없으면
            self.add_log_entry("• 메시 관련 검사... 대상 없음", passed=True) # 로그에 대상이 없다고 기록합니다.
            if not unknown_nodes: # 알 수 없는 노드도 없을 경우에만
                self.result_list.addItem("검사할 대상(Mesh)이 없습니다.") # 문제 항목 리스트에 메시지를 표시합니다.
            return # 함수 실행을 종료합니다.

        # 실행할 검사 목록을 데이터 기반으로 정의합니다.
        checks_to_run = [
            {"name": "이름 규칙", "header": "--- Naming Issues ---", "func": self.core.check_naming_conventions},
            {"name": "히스토리", "header": "--- Histroy Detected ---", "func": self.core.check_history},
            {"name": "트랜스폼 동결", "header": "--- Unfrozen Transforms ---", "func": self.core.check_freeze_transforms},
            {"name": "다중 UV 세트", "header": "--- UV Set Issues ---", "func": self.core.check_multi_uvsets},
            {"name": "UV 오버랩", "header": "--- UV Overlap (Faces) ---", "func": self.core.check_uv_overlapping},
            {"name": "메시 에러", "header": "--- Mesh Errors (NGons, Non-manifold) ---", "func": self.core.check_mesh_errors},
            {"name": "UV 할당 에러", "header": "--- UV Errors (Missing, Unassigned) ---", "func": self.core.check_uv_errors},
        ]

        # 정의된 검사 목록을 순회하며 실행합니다.
        for check in checks_to_run:
            errors = check["func"](targets) # 검사 함수를 실행하여 에러 목록을 받습니다.
            if errors: # 에러가 있으면
                self.add_log_entry(f"• {check['name']} 검사... 실패 ({len(errors)}개)", passed=False) # 로그에 실패로 기록합니다.
                self.add_selection_header(check["header"]) # 문제 항목 리스트에 헤더를 추가합니다.
                for e in errors: # 각 에러에 대해
                    self.result_list.addItem(e) # 문제 항목 리스트에 추가합니다.
            else: # 에러가 없으면
                self.add_log_entry(f"• {check['name']} 검사... 통과", passed=True) # 로그에 통과로 기록합니다.

        # 검사 결과 아무런 문제가 없으면 메시지를 표시합니다.
        if self.result_list.count() == 0: # 문제 항목 리스트에 아무것도 없으면
            self.result_list.addItem("모든 검사를 통과했습니다.") # 통과 메시지를 추가합니다.

    def sync_selection_to_maya(self):
        """
        UI 리스트의 선택 상태를 Maya 씬의 실제 오브젝트 선택과 동기화합니다.
        """
        selected_items = self.result_list.selectedItems() # 리스트에서 선택된 아이템들을 가져옵니다.
        to_select = [] # Maya에서 선택할 오브젝트들을 담을 리스트입니다.

        for item in selected_items: # 선택된 각 아이템에 대해
            text = item.text() # 아이템의 텍스트를 가져옵니다.

            if text.startswith("---"): # 텍스트가 헤더이면
                continue # 다음 아이템으로 넘어갑니다.

            # e.g. "pCube1 (Multiple UV Sets: 2)" -> "pCube1"
            clean_name = text.split('(')[0].strip() # 텍스트에서 실제 오브젝트 이름만 추출합니다.
            if cmds.objExists(clean_name): # 해당 이름의 오브젝트가 씬에 존재하면
                to_select.append(clean_name) # 선택할 목록에 추가합니다.

        if to_select: # 선택할 오브젝트가 있으면
            cmds.select(to_select, replace=True) # 해당 오브젝트들을 선택합니다.
        else: # 선택할 오브젝트가 없으면
            cmds.select(clear=True) # 씬의 선택을 해제합니다.

    def run_fix_selected(self):
        """
        리스트에서 선택된 항목들에 대한 수정을 진행합니다.
        """
        selected_items = self.result_list.selectedItems() # 리스트에서 선택된 아이템들을 가져옵니다.
        if not selected_items: # 선택된 아이템이 없으면
            QtWidgets.QMessageBox.warning(self, "알림", "수정할 노드를 리스트에서 선택하세요") # 경고 메시지를 표시합니다.
            return # 함수 실행을 종료합니다.

        fixes_to_run = {}  # {수정 함수: [대상 노드1, 대상 노드2]} 형식의 딕셔너리
        run_unknown_node_cleanup = False # 알 수 없는 노드 수정 플래그

        for item in selected_items: # 선택된 각 아이템에 대해
            if item.text().startswith("---"): # 아이템이 헤더이면
                continue # 건너뜁니다.

            current_row = self.result_list.row(item) # 현재 아이템의 행 번호를 가져옵니다.
            header_text = "" # 헤더 텍스트를 저장할 변수입니다.
            for i in range(current_row, -1, -1): # 현재 행부터 위로 올라가며
                header_item = self.result_list.item(i) # 해당 행의 아이템을 가져옵니다.
                if header_item.text().startswith("---"): # 아이템이 헤더이면
                    header_text = header_item.text() # 헤더 텍스트를 저장하고
                    break # 반복을 멈춥니다.

            # 'Unknown Nodes' 헤더는 특별히 처리합니다.
            if header_text == "--- Unknown Nodes ---": # 알 수 없는 노드 카테고리이면
                run_unknown_node_cleanup = True # 플래그를 True로 설정합니다.
                continue # 다음 아이템으로 넘어갑니다.

            fix_function = self.fix_map.get(header_text) # 헤더에 해당하는 수정 함수를 맵에서 찾습니다.
            if fix_function: # 수정 함수가 존재하면
                if fix_function not in fixes_to_run: # 딕셔너리에 해당 함수가 아직 없으면
                    fixes_to_run[fix_function] = [] # 새로운 리스트를 생성하여 추가합니다.
                
                node_name = item.text() # 아이템의 텍스트(노드 이름)를 가져옵니다.
                fixes_to_run[fix_function].append(node_name) # 해당 함수의 노드 목록에 추가합니다.

        if not fixes_to_run and not run_unknown_node_cleanup: # 실행할 수정 작업이 없으면
            QtWidgets.QMessageBox.information(self, "알림", "선택된 항목에 대한 자동 수정 기능이 없습니다.") # 정보 메시지를 표시합니다.
            return # 함수 실행을 종료합니다.

        if run_unknown_node_cleanup: # 알 수 없는 노드 수정 플래그가 켜져 있으면
            removed = self.core.cleanup_unknown_nodes() # 모든 알 수 없는 노드를 삭제하는 함수를 실행합니다.
            print(f"{len(removed)}개의 Unknown 노드를 삭제했습니다.") # 스크립트 에디터에 삭제된 노드 수를 출력합니다.

        for function, nodes in fixes_to_run.items(): # 실행할 수정 함수 목록을 순회합니다.
            clean_nodes = [n.split('(')[0].strip() for n in nodes] # 텍스트에서 순수 노드 이름만 추출합니다.
            function(list(set(clean_nodes))) # 중복을 제거한 노드 리스트를 인자로 하여 수정 함수를 실행합니다.

        self.run_full_check() # 모든 수정이 끝난 후, 씬을 다시 검사하여 결과를 갱신합니다.

    def run_fix_all(self):
        """
        리스트에 있는 모든 수정 가능한 항목들을 자동으로 수정합니다.
        """
        if self.result_list.count() == 0 or (self.result_list.count() == 1 and "검사할" in self.result_list.item(0).text()):
            QtWidgets.QMessageBox.information(self, "알림", "수정할 항목이 없습니다.") # 정보 메시지를 표시합니다.
            return # 함수 실행을 종료합니다.

        reply = QtWidgets.QMessageBox.question(self, '확인',
                                           "모든 자동 수정 가능한 항목을 수정하시겠습니까?\n이 작업은 되돌릴 수 없습니다.",
                                           QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.No: # 사용자가 'No'를 선택하면
            return # 함수 실행을 종료합니다.

        fixes_to_run = {} # 실행할 수정 함수들을 담을 딕셔너리입니다.
        run_unknown_node_cleanup = False # 알 수 없는 노드 수정 플래그입니다.

        for row in range(self.result_list.count()):
            item = self.result_list.item(row) # 해당 행의 아이템을 가져옵니다.
            item_text = item.text() # 아이템의 텍스트를 가져옵니다.
            if item_text.startswith("---"): # 아이템이 헤더이면
                continue # 건너뜁니다.

            header_text = ""
            for i in range(row, -1, -1):
                header_item = self.result_list.item(i)
                if header_item.text().startswith("---"):
                    header_text = header_item.text()
                    break

            if header_text == "--- Unknown Nodes ---": # 알 수 없는 노드 카테고리이면
                run_unknown_node_cleanup = True # 플래그를 켭니다.
                continue # 다음 아이템으로 넘어갑니다.

            fix_function = self.fix_map.get(header_text) # 헤더에 해당하는 수정 함수를 찾습니다.
            if fix_function: # 수정 함수가 있으면
                if fix_function not in fixes_to_run: # 딕셔너리에 함수가 없으면
                    fixes_to_run[fix_function] = [] # 새로 추가합니다.
                node_name = item_text # 아이템 텍스트(노드 이름)를 가져옵니다.
                fixes_to_run[fix_function].append(node_name) # 해당 함수의 노드 목록에 추가합니다.

        if run_unknown_node_cleanup: # 알 수 없는 노드 수정이 필요하면
            self.core.cleanup_unknown_nodes() # 해당 함수를 실행합니다.

        for function, nodes in fixes_to_run.items(): # 다른 모든 수정 작업을 순회하며
            clean_nodes = [n.split('(')[0].strip() for n in nodes] # 노드 이름을 정리하고
            function(list(set(clean_nodes))) # 수정 함수를 실행합니다.

        QtWidgets.QMessageBox.information(self, "완료", "모든 수정 가능한 항목에 대한 수정이 완료되었습니다.")
        self.run_full_check() # 씬을 다시 검사하여 결과를 갱신합니다.

def main():
    """
    UI를 실행하는 메인 함수입니다.
    이전 창이 열려있으면 닫고 새로 생성하여 보여줍니다.
    """
    global validator_window # UI 인스턴스를 전역 변수로 관리합니다.
    try:
        validator_window.close() # 기존에 열려있는 창을 닫습니다.
        validator_window.deleteLater() # 메모리에서 완전히 삭제되도록 예약합니다.
    except:
        pass # 창이 없는 경우 예외를 무시합니다.
    validator_window = SceneValidatorUI() # 새 UI 인스턴스를 생성합니다.
    validator_window.show(dockable=True) # 도킹 가능한 형태로 창을 보여줍니다.


if __name__ == "__main__":
    main() # 스크립트가 직접 실행될 때 main 함수를 호출합니다.