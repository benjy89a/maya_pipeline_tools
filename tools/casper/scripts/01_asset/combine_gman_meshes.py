"""
========================================================
combine_gman_meshes.py
========================================================

[기능]
- Gman 캐릭터의 머리 메시와 몸통 메시를 선택된 버텍스들을 기준으로 정확하게 결합(Combine)하고 병합(Merge)합니다.
- `maya.api.OpenMaya` (om2)를 사용하여 대량의 버텍스 처리 시의 성능을 최적화했습니다.
- 사용자가 직접 머리 메시와 몸통 메시의 연결될 버텍스들을 지정하여 의도하지 않은 병합을 방지합니다.

[작동 원리]
1. 사용자가 UI를 통해 머리 메시와 몸통 메시에서 연결될 버텍스 목록을 각각 선택합니다.
2. 원본 메쉬들을 복사하여 새로운 결합 메쉬를 생성합니다.
3. `om2`를 사용하여 결합된 메쉬 내에서 사용자가 선택한 버텍스들의 월드 위치에 가장 가까운 버텍스를 고속으로 찾아냅니다.
4. 찾아낸 버텍스 쌍들을 `polyMergeVertex` 명령으로 병합하여 두 메쉬를 연결합니다.

[실행 방법]
1. Maya 씬에 머리 메쉬와 몸통 메쉬를 준비합니다.
2. 머리 메쉬에서 몸통과 연결될 부분의 버텍스들을 선택합니다. (예: 목 부분)
3. 몸통 메쉬에서 머리와 연결될 부분의 버텍스들을 선택합니다. (예: 목 부분)
4. 스크립트를 실행하고, UI에서 'Get Head Vertices'와 'Get Body Vertices' 버튼을 클릭하여 선택된 버텍스들을 가져옵니다.
5. 적절한 'Merge Threshold' 값을 설정합니다.
6. 'Run Combine' 버튼을 클릭하여 메쉬를 결합하고 버텍스를 병합합니다.

[주의 사항]
- 머리 버텍스와 몸통 버텍스의 개수는 동일해야 합니다.
- 머리 메쉬와 몸통 메쉬는 서로 다른 오브젝트여야 합니다.
"""

from PySide2 import QtWidgets, QtCore
import maya.cmds as mc
import maya.api.OpenMaya as om2
import shiboken2
import maya.OpenMayaUI as omui


def get_maya_main_window():
    """마야의 메인 윈도우를 PySide2 윈도우로 변환하여 반환"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)



class GmanCombineUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_main_window()):
        super(GmanCombineUI, self).__init__(parent)
        self.setWindowTitle("Combine Gman Meshes Tool") # UI 타이틀 변경
        self.setFixedSize(300, 320)  # 창 크기 조정
        self.setup_ui()
        self.create_connections()

    def setup_ui(self):
        """UI를 설정합니다."""
        # 레이아웃 설정
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # 머리 연결 버텍스 입력
        self.head_vtx_label = QtWidgets.QLabel("Head Connection Vertices:")
        self.head_vtx_input = QtWidgets.QLineEdit()
        self.head_vtx_input.setPlaceholderText("Select head vertices and click button below")
        self.get_head_vtx_button = QtWidgets.QPushButton("Get Head Vertices")

        # 몸통 연결 버텍스 입력
        self.body_vtx_label = QtWidgets.QLabel("Body Connection Vertices:")
        self.body_vtx_input = QtWidgets.QLineEdit()
        self.body_vtx_input.setPlaceholderText("Select body vertices and click button below")
        self.get_body_vtx_button = QtWidgets.QPushButton("Get Body Vertices")

        # 머지 거리 (Threshold)
        self.threshold_label = QtWidgets.QLabel("Merge Threshold:")
        self.threshold_input = QtWidgets.QDoubleSpinBox()
        self.threshold_input.setRange(0.001, 1.0)
        self.threshold_input.setSingleStep(0.01)
        self.threshold_input.setValue(0.01)

        # 실행 버튼
        self.run_button = QtWidgets.QPushButton("Run Combine")

        # 레이아웃 구성
        self.main_layout.addWidget(self.head_vtx_label)
        self.main_layout.addWidget(self.head_vtx_input)
        self.main_layout.addWidget(self.get_head_vtx_button)
        self.main_layout.addSpacing(10) # 간격 추가
        self.main_layout.addWidget(self.body_vtx_label)
        self.main_layout.addWidget(self.body_vtx_input)
        self.main_layout.addWidget(self.get_body_vtx_button)
        self.main_layout.addSpacing(10) # 간격 추가
        self.main_layout.addWidget(self.threshold_label)
        self.main_layout.addWidget(self.threshold_input)
        self.main_layout.addWidget(self.run_button)

    def create_connections(self):
        """버튼과 동작 연결."""
        self.get_head_vtx_button.clicked.connect(self.get_selected_head_vertices)
        self.get_body_vtx_button.clicked.connect(self.get_selected_body_vertices)
        self.run_button.clicked.connect(self.run_gman_combine)

    def get_selected_head_vertices(self):
        """선택된 머리 버텍스를 가져와 UI 입력란에 표시."""
        selection = mc.ls(selection=True, flatten=True)
        # 컴포넌트인지 확인 (버텍스, 엣지, 페이스)
        if selection and ".vtx[" in selection[0]:
            self.head_vtx_input.setText(",".join(selection))
        else:
            mc.warning("No vertices selected for Head!")

    def get_selected_body_vertices(self):
        """선택된 몸통 버텍스를 가져와 UI 입력란에 표시."""
        selection = mc.ls(selection=True, flatten=True)
        # 컴포넌트인지 확인 (버텍스, 엣지, 페이스)
        if selection and ".vtx[" in selection[0]:
            self.body_vtx_input.setText(",".join(selection))
        else:
            mc.warning("No vertices selected for Body!")

    def run_gman_combine(self):
        """Combine 스크립트 실행."""
        # 입력값 가져오기
        head_vertices = self.head_vtx_input.text().split(",")
        body_vertices = self.body_vtx_input.text().split(",")
        threshold = self.threshold_input.value()

        # 입력값 유효성 검사
        if not head_vertices[0] or not body_vertices[0]:
            mc.warning("Please provide vertices for both Head and Body.")
            return
        
        if len(head_vertices) != len(body_vertices):
            mc.warning("The number of vertices for Head and Body must be the same.")
            return

        # combine_gman_meshes_tool 실행
        try:
            combine_gman_meshes(head_vertices, body_vertices, threshold)
        except Exception as e:
            mc.error(f"Error during combine_gman_meshes: {e}")


def combine_gman_meshes(head_vertices, body_vertices, threshold=0.01):
    """
    Gman Meshes Combine의 핵심 기능. 두 메쉬의 지정된 연결부 버텍스를 병합합니다.
    om2를 사용하여 성능을 최적화합니다.
    """
    # 1. 유효성 검사
    if not head_vertices or not body_vertices:
        mc.error("머리와 몸통의 버텍스 목록을 모두 제공해야 합니다.")
        return

    if len(head_vertices) != len(body_vertices):
        mc.error("머리와 몸통의 버텍스 개수가 동일해야 합니다.")
        return

    # 2. 메쉬 정보 추출 및 복사
    head_mesh = head_vertices[0].split('.')[0]
    body_mesh = body_vertices[0].split('.')[0]
    
    if head_mesh == body_mesh:
        mc.error("머리와 몸통은 서로 다른 메쉬여야 합니다.")
        return

    head_copy = mc.duplicate(head_mesh, name=f"{head_mesh}_copy")[0]
    body_copy = mc.duplicate(body_mesh, name=f"{body_mesh}_copy")[0]

    # 원본 버텍스들의 월드 공간 위치 저장
    head_positions = [mc.pointPosition(v, world=True) for v in head_vertices]
    body_positions = [mc.pointPosition(v, world=True) for v in body_vertices]

    # 3. 메쉬 결합
    combined_mesh = mc.polyUnite(head_copy, body_copy, name="combined_gman_mesh")[0] # 메쉬 이름 변경
    mc.delete(combined_mesh, constructionHistory=True)

    # 4. om2를 사용한 빠르고 정확한 버텍스 인덱스 검색
    selection_list = om2.MSelectionList()
    selection_list.add(combined_mesh)
    dag_path = selection_list.getDagPath(0)
    mfn_mesh = om2.MFnMesh(dag_path)

    # 결합된 메쉬의 모든 버텍스 위치를 한 번에 가져옴 (성능 핵심)
    all_vtx_positions = mfn_mesh.getPoints(om2.MSpace.kWorld)

    def find_closest_vtx_index(target_pos, vtx_positions):
        """
        주어진 위치(target_pos)에 가장 가까운 버텍스의 인덱스를 찾습니다.
        """
        target_point = om2.MPoint(target_pos)
        min_dist_sq = float('inf')
        closest_idx = -1
        for i, pos in enumerate(vtx_positions):
            dist_sq = target_point.distanceTo(pos)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_idx = i
        return closest_idx

    # 5. 버텍스 병합
    merge_count = 0
    for i in range(len(head_positions)):
        head_pos = head_positions[i]
        body_pos = body_positions[i]

        # 결합된 메쉬에서 원본 버텍스 위치에 해당하는 새 인덱스 찾기
        head_idx = find_closest_vtx_index(head_pos, all_vtx_positions)
        body_idx = find_closest_vtx_index(body_pos, all_vtx_positions)

        if head_idx != -1 and body_idx != -1 and head_idx != body_idx:
            vtx1 = f"{combined_mesh}.vtx[{head_idx}]"
            vtx2 = f"{combined_mesh}.vtx[{body_idx}]"
            mc.polyMergeVertex([vtx1, vtx2], distance=threshold)
            merge_count += 1
            # 병합 후에는 버텍스 정보가 변경될 수 있으므로, 전체 위치를 다시 가져오는 것이 가장 안정적입니다.
            # 이 작업은 성능에 영향을 줄 수 있지만, 정확성을 보장합니다.
            all_vtx_positions = mfn_mesh.getPoints(om2.MSpace.kWorld)


    # 6. 최종 처리
    mc.select(combined_mesh)
    mc.delete(combined_mesh, constructionHistory=True)

    # 7. 결과 출력
    print(f"총 {len(head_positions)}개의 연결점 중 {merge_count}개를 병합했습니다.")
    if merge_count == len(head_positions):
        print("모든 연결점이 성공적으로 병합되었습니다!")
    else:
        print(f"경고: 일부 버텍스가 병합되지 않았을 수 있습니다. Threshold 값을 확인하세요.")

# UI 실행
def show_ui():
    global gman_combine_ui
    try:
        gman_combine_ui.close()  # 기존 UI 닫기
    except:
        pass
    gman_combine_ui = GmanCombineUI()
    gman_combine_ui.show()


show_ui()
