# -*- coding: utf-8 -*-
"""
================================================================================
Casper | Maya 스크립트 런처
================================================================================

[요약]
Maya 사용자를 위한 도킹 가능한 스크립트 런처입니다. 지정된 폴더 구조를 기반으로
탭으로 정리된 UI를 동적으로 생성하여, 아티스트와 TD가 스크립트에 효율적으로
접근하고 실행할 수 있도록 돕습니다.

[기능]
- 지정된 폴더와 그 하위 폴더의 .py 스크립트 목록을 탭으로 구분하여 UI에 표시합니다.
- 스크립트 버튼을 좌클릭하면 스크립트를 실행하고, 우클릭하면 해당 스크립트의 도움말(docstring)을 표시합니다.
- 마지막으로 사용한 폴더 경로를 'casper_config.config'에 자동 저장하여 다음 실행 시 자동으로 로드합니다.
- '폴더 변경' 버튼을 통해 언제든지 스크립트 루트 폴더를 변경하고 저장할 수 있습니다.
- UI는 Maya 인터페이스에 도킹 가능하며, Maya 종료 시 함께 닫힙니다.
- 상세한 에러 로그, 새로고침, 스크롤 등 다양한 편의 기능을 제공합니다.

[실행 방법]
Maya 스크립트 에디터에서 이 파일의 모든 코드를 실행하거나,
아래의 `launch()` 함수를 호출하세요.

launch()
"""

import os
import sys
import traceback
import random
import ast
import functools

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QMessageBox, QScrollArea, QTabWidget
)
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.utils
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


# --- Maya 연동 유틸리티 ---
def get_maya_main_window():
    """Maya의 메인 윈도우 위젯을 QWidget 형태로 반환합니다."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr:
        return wrapInstance(int(main_window_ptr), QWidget)
    return None


# --- 커스텀 UI 위젯 ---
class CustomScriptButton(QPushButton):
    """
    좌클릭과 우클릭을 구분하여 각각 다른 동작을 처리할 수 있는 커스텀 버튼 클래스입니다.
    우클릭 시 `rightClicked` 시그널을 발생시킵니다.
    """
    rightClicked = Signal(str)

    def __init__(self, text, script_path, parent=None):
        """
        CustomScriptButton의 생성자입니다.

        Args:
            text (str): 버튼에 표시될 텍스트입니다.
            script_path (str): 버튼에 연결될 스크립트의 전체 경로입니다.
            parent (QWidget, optional): 부모 위젯. Defaults to None.
        """
        super(CustomScriptButton, self).__init__(text, parent)
        self.script_path = script_path

    def mousePressEvent(self, event):
        """마우스 클릭 이벤트를 재정의하여 우클릭을 감지합니다."""
        # 마우스 우클릭 시, 'rightClicked' 시그널을 발생시킵니다.
        if event.button() == Qt.RightButton:
            self.rightClicked.emit(self.script_path)
        # 그 외의 클릭(좌클릭 등)은 기본 QPushButton의 동작을 따릅니다.
        else:
            super(CustomScriptButton, self).mousePressEvent(event)


# --- 메인 UI 클래스 ---
class ScriptRunner(MayaQWidgetDockableMixin, QWidget):
    """
    스크립트 런처의 메인 UI 클래스입니다.
    UI 구성, 스크립트 스캔, 사용자 상호작용 처리 등 모든 핵심 기능을 담당합니다.
    MayaQWidgetDockableMixin을 상속받아 Maya 내에서 도킹 가능한 위젯으로 동작합니다.
    """
    # --- 클래스 상수 선언 ---
    # 마지막으로 사용한 폴더 경로를 저장하는 설정 파일의 경로
    CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "casper_config.config")
    
    # 버튼에 무작위로 적용될 색상 목록
    BUTTON_COLORS = ["#555555", "#666666", "#4a6a7f", "#7f6c4a", "#4f7f4a"]

    # 스크립트 스캔 시 무시할 폴더 및 파일 목록
    IGNORE_FOLDERS = {"__pycache__", ".git", ".venv", ".vscode", "icons"}
    IGNORE_FILES = {"__init__.py"}

    def __init__(self, folder_path, parent=get_maya_main_window()):
        """
        ScriptRunner UI의 생성자입니다.

        Args:
            folder_path (str): 스크립트를 스캔할 루트 폴더의 경로.
            parent (QWidget, optional): 부모 위젯. 기본값은 Maya 메인 윈도우입니다.
        """
        super(ScriptRunner, self).__init__(parent)
        self.folder_path = folder_path

        # --- 윈도우 설정 및 레이아웃 구성 ---
        self.setWindowTitle("Casper Script Runner")
        self.setGeometry(300, 200, 450, 550)  # 초기 윈도우 크기 설정
        main_layout = QVBoxLayout(self)

        # --- 상단 UI (경로 표시, 폴더 변경, 새로고침 버튼) ---
        top_layout = QHBoxLayout()
        self.label = QLabel(f"📁 루트 폴더: {self.folder_path}")
        self.label.setWordWrap(True)

        change_folder_btn = QPushButton("📂 폴더 변경")
        change_folder_btn.clicked.connect(self.change_folder)

        refresh_btn = QPushButton("🔄 새로고침")
        refresh_btn.clicked.connect(self.refresh_scripts)

        top_layout.addWidget(self.label, 1)  # 라벨이 남는 공간을 모두 차지하도록 설정
        top_layout.addWidget(change_folder_btn)
        top_layout.addWidget(refresh_btn)
        main_layout.addLayout(top_layout)

        # --- 스크립트 버튼들이 표시될 탭 위젯 ---
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #333; background-color: #3a3a3a; }
            QTabBar::tab { background: #454545; border: 1px solid #333; border-bottom-color: #3a3a3a; border-top-left-radius: 4px; border-top-right-radius: 4px; padding: 5px 10px; color: #ccc; font-weight: bold; }
            QTabBar::tab:selected { background: #606060; border-color: #333; border-bottom-color: #606060; color: white; }
            QTabBar::tab:hover { background: #505050; }
        """)
        main_layout.addWidget(self.tab_widget)

        # UI가 생성될 때 스크립트를 처음 로드합니다.
        self.load_scripts()

    @staticmethod
    def read_config():
        """설정 파일에서 마지막으로 사용한 폴더 경로를 읽어옵니다."""
        if os.path.exists(ScriptRunner.CONFIG_FILE_PATH):
            with open(ScriptRunner.CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                return f.read().strip()
        return None

    @staticmethod
    def write_config(path):
        """주어진 폴더 경로를 설정 파일에 저장합니다."""
        with open(ScriptRunner.CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(path)

    @staticmethod
    def _extract_docstring(file_path):
        """
        AST(Abstract Syntax Trees)를 사용하여 Python 스크립트 파일을 직접 실행하지 않고
        안전하게 최상위 독스트링(docstring)을 추출합니다.

        Args:
            file_path (str): 분석할 Python 스크립트 파일의 경로.

        Returns:
            str: 추출된 독스트링. 실패 시 빈 문자열을 반환합니다.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # 파일 내용을 AST로 파싱합니다.
                tree = ast.parse(f.read())
            # 파싱된 트리에서 독스트링을 추출합니다.
            return ast.get_docstring(tree)
        except Exception:
            # 파싱 중 에러 발생 시 빈 문자열을 반환합니다.
            return ""
            
    def change_folder(self):
        """
        폴더 선택 대화상자를 열어 새로운 스크립트 루트 폴더를 선택하고,
        선택된 경로를 설정 파일에 저장한 후 UI를 새로고침합니다.
        """
        new_folder = QFileDialog.getExistingDirectory(self, "새로운 스크립트 루트 폴더를 선택하세요", self.folder_path)
        if new_folder and new_folder != self.folder_path:
            self.folder_path = new_folder
            ScriptRunner.write_config(new_folder)  # 새로운 경로 저장
            self.label.setText(f"📁 루트 폴더: {new_folder}")
            self.refresh_scripts()

    def _create_script_tab(self, target_folder, tab_name):
        """
        지정된 폴더 내의 스크립트들을 찾아 UI에 새 탭과 버튼들을 생성합니다.

        Args:
            target_folder (str): .py 파일을 스캔할 폴더 경로.
            tab_name (str): UI 탭에 표시될 이름.
        """
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        scroll_widget = QWidget()
        button_layout = QVBoxLayout(scroll_widget)
        button_layout.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(scroll_widget)

        try:
            # 폴더 내에서 유효한 .py 파일들을 찾아 정렬합니다.
            py_files = sorted(
                [f for f in os.listdir(target_folder) if f.endswith(".py") and f not in self.IGNORE_FILES],
                key=str.lower
            )

            if not py_files:
                button_layout.addWidget(QLabel("⚠️ 이 폴더에 실행할 .py 파일이 없습니다."))
            else:
                # 각 스크립트 파일에 대해 버튼을 생성합니다.
                for f in py_files:
                    color = random.choice(self.BUTTON_COLORS)
                    full_script_path = os.path.join(target_folder, f)
                    display_name = os.path.splitext(f)[0]

                    btn = CustomScriptButton(f"▶ {display_name}", full_script_path)
                    btn.setStyleSheet(f"background-color: {color}; color: white; font-size: 12pt; padding: 5px;")
                    
                    # 좌클릭(clicked)과 우클릭(rightClicked) 시그널을 각 함수에 연결합니다.
                    btn.clicked.connect(functools.partial(self.run_script, full_script_path))
                    btn.rightClicked.connect(self.show_script_help)
                    
                    button_layout.addWidget(btn)
        except Exception as e:
            button_layout.addWidget(QLabel(f"🚫 폴더를 읽는 중 에러 발생:\n{e}"))

        self.tab_widget.addTab(scroll_area, tab_name)
        
    def refresh_scripts(self):
        """UI의 모든 탭을 지우고 현재 루트 폴더에서 스크립트를 다시 로드합니다."""
        self.tab_widget.clear()
        self.load_scripts()
        print("스크립트 목록을 새로고침했습니다.")

    def load_scripts(self):
        """
        루트 폴더와 그 바로 아래 하위 폴더들을 스캔하여 UI 탭과 버튼들을 구성합니다.
        """
        # 1. 루트 폴더에 대한 탭을 먼저 생성합니다.
        root_folder_name = os.path.basename(self.folder_path)
        self._create_script_tab(self.folder_path, f"📁 {root_folder_name}")

        try:
            # 2. 유효한 하위 폴더들을 찾아 정렬합니다.
            subfolders = sorted(
                [d for d in os.listdir(self.folder_path) if
                 os.path.isdir(os.path.join(self.folder_path, d)) and d not in self.IGNORE_FOLDERS],
                key=str.lower
            )
            # 3. 각 하위 폴더에 대한 탭을 생성합니다.
            for folder in subfolders:
                full_folder_path = os.path.join(self.folder_path, folder)
                self._create_script_tab(full_folder_path, f"📂 {folder}")
        except Exception as e:
            QMessageBox.critical(self, "폴더 스캔 에러", f"하위 폴더를 스캔하는 중 에러가 발생했습니다:\n{str(e)}")

    def run_script(self, script_path):
        """
        주어진 경로의 Python 스크립트를 Maya의 메인 스레드에서 안전하게 실행합니다.

        Args:
            script_path (str): 실행할 스크립트의 전체 경로.
        """
        filename = os.path.basename(script_path)
        if not os.path.exists(script_path):
            QMessageBox.warning(self, "파일 없음", f"{filename} 파일을 찾을 수 없습니다.")
            return

        print(f"'{filename}' 스크립트 실행을 시작합니다... (경로: {script_path})")

        # 스크립트가 독립적으로 실행될 수 있도록 깨끗한 전역(global) 환경을 만들어줍니다.
        script_globals = {
            "__name__": "__main__",
            "__file__": script_path,
        }

        try:
            # 실제 실행 로직을 담은 함수를 정의합니다.
            def _execute():
                with open(script_path, "r", encoding="utf-8") as f:
                    code = f.read()
                exec(code, script_globals)

            # Maya의 유틸리티를 사용하여 메인 스레드에서 코드를 실행합니다. (UI 관련 충돌 방지)
            maya.utils.executeInMainThreadWithResult(_execute)
            print(f"'{filename}' 스크립트 실행이 완료되었습니다.")
        except Exception:
            # 스크립트 실행 중 발생하는 모든 예외를 처리하고 사용자에게 상세히 보고합니다.
            detailed_error_message = traceback.format_exc()
            print(f"'{filename}' 실행 중 에러 발생:\n{detailed_error_message}")
            QMessageBox.critical(self, "스크립트 실행 에러", f"'{filename}' 실행 중 에러가 발생했습니다:\n\n{detailed_error_message}")

    def show_script_help(self, script_path):
        """
        스크립트 파일의 독스트링(docstring)을 추출하여 도움말 메시지 박스로 보여줍니다.

        Args:
            script_path (str): 도움말을 확인할 스크립트의 전체 경로.
        """
        filename = os.path.basename(script_path)
        docstring = ScriptRunner._extract_docstring(script_path)

        if not docstring:
            docstring = "이 스크립트에는 작성된 도움말(docstring)이 없습니다."

        QMessageBox.information(self, f"'{filename}' 도움말", docstring)


# --- 전역 인스턴스 관리 및 실행 함수 ---
casper_runner_instance = None

def launch():
    """
    Casper 스크립트 런처를 시작하는 메인 함수입니다.
    기존에 실행된 인스턴스를 관리하고, UI를 생성 및 표시합니다.
    """
    global casper_runner_instance

    # 만약 이전에 실행된 UI 인스턴스가 있다면, 새로 만들기 전에 먼저 닫습니다.
    if casper_runner_instance:
        try:
            casper_runner_instance.close()
            casper_runner_instance.deleteLater()
        except Exception:
            pass  # 창이 이미 닫혔을 경우 발생할 수 있는 오류를 무시합니다.

    # --- 환경 설정: 프로젝트 루트 경로를 Python 경로에 추가 ---
    # 다른 스크립트에서 프로젝트 내의 모듈을 임포트할 수 있도록 경로를 설정합니다.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"프로젝트 루트 경로를 sys.path에 추가했습니다: {project_root}")

    # --- 폴더 경로 결정 로직 ---
    # 1. 설정 파일에서 마지막으로 사용한 폴더를 읽어옵니다.
    folder_to_load = ScriptRunner.read_config()

    # 2. 설정 파일이 없거나 경로가 유효하지 않으면, 사용자에게 직접 폴더를 선택하도록 요청합니다.
    if not folder_to_load or not os.path.isdir(folder_to_load):
        folder_to_load = QFileDialog.getExistingDirectory(get_maya_main_window(), "스크립트가 들어있는 루트 폴더를 선택하세요")

    # --- UI 실행 ---
    if folder_to_load:
        # 다음 세션을 위해 선택된 경로를 저장합니다.
        ScriptRunner.write_config(folder_to_load)
        
        # UI 인스턴스를 생성하고 화면에 표시합니다.
        casper_runner_instance = ScriptRunner(folder_to_load)
        casper_runner_instance.show(dockable=True, floating=True, area='right', label='Casper Runner')
    else:
        print("Casper 실행기: 폴더가 선택되지 않아 실행을 취소했습니다.")
