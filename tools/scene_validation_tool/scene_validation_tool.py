import maya.cmds as cmds
import os
import configparser

class SceneValidatorCore:
    """
    모델링 데이터 검증을 위한 핵심 로직을 담고 있는 클래스입니다.
    이 클래스는 UI와 분리되어 있으며, 각 검증 항목을 메소드로 제공합니다.
    """
    def __init__(self):
        """
        SceneValidatorCore 클래스의 생성자입니다.
        'naming_convention.config' 설정 파일을 읽어 검증 규칙을 초기화합니다.
        """
        self.config = configparser.ConfigParser()
        # 현재 스크립트 파일의 디렉토리 경로를 가져옵니다.
        # __file__은 이 스크립트 파일의 전체 경로를 나타냅니다.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'naming_convention.config')

        # 기본 접미사 설정 (config 파일이 없을 경우 대비)
        self.mesh_suffix = '_geo'

        # 설정 파일이 존재하는지 확인하고 읽습니다.
        if os.path.exists(config_path):
            self.config.read(config_path)
            # 'naming_convention' 섹션에서 'mesh_suffix' 값을 가져옵니다.
            # fallback 옵션을 사용하여 값이 없을 경우 기본값을 사용하도록 할 수 있습니다.
            self.mesh_suffix = self.config.get('naming_convention', 'mesh_suffix', fallback='_geo')
        else:
            # 설정 파일이 없는 경우 사용자에게 경고 메시지를 출력합니다.
            cmds.warning(f"설정 파일을 찾을 수 없습니다: {config_path}. 기본 접미사 '{self.mesh_suffix}'를 사용합니다.")

    def get_all_mesh_transforms(self):
        """
        씬에 있는 모든 메쉬의 트랜스폼 노드를 수집합니다.
        중간 계산용(intermediate) 메쉬는 제외됩니다.

        :return: 씬에 있는 모든 메쉬 트랜스폼 노드의 리스트
        :rtype: list
        """
        all_meshes = cmds.ls(type='mesh', long=True) or []
        valid_transforms = []
        for mesh in all_meshes:
            # intermediateObject는 렌더링되지 않는 중간 형태이므로 검사에서 제외합니다.
            if cmds.getAttr(f"{mesh}.intermediateObject"):
                continue
            parent = cmds.listRelatives(mesh, parent=True, fullPath=True)
            if parent:
                valid_transforms.append(parent[0])
        return list(set(valid_transforms))

    def check_naming_conventions(self, nodes):
        """
        [검증] 네이밍 규칙
        - 지오메트리 그룹 이름이 config 파일에 지정된 접미사로 끝나는지 검사합니다.

        :param nodes: 검사할 트랜스폼 노드 리스트
        :return: 규칙에 맞지 않는 노드 리스트
        :rtype: list
        """
        invalid_names = []
        for node in nodes:
            name_only = node.split('|')[-1]
            if not name_only.endswith(self.mesh_suffix):
                invalid_names.append(node)
        return list(set(invalid_names))

    def check_freeze_transforms(self, nodes):
        """
        [검증] Freeze Transform (변환 값 초기화)
        - Translate, Rotate 값이 0인지 확인합니다.
        - Scale 값이 1인지 확인합니다.

        :param nodes: 검사할 트랜스폼 노드 리스트
        :return: Transform이 Freeze되지 않은 노드 리스트
        :rtype: list
        """
        unfrozen = []
        for node in nodes:
            t = cmds.getAttr(f"{node}.translate")[0]
            r = cmds.getAttr(f"{node}.rotate")[0]
            s = cmds.getAttr(f"{node}.scale")[0]

            # 0.0001과 같은 작은 오차 범위를 허용합니다.
            is_translated = any(abs(v) > 0.0001 for v in t)
            is_rotated = any(abs(v) > 0.0001 for v in r)
            is_scaled = any(abs(v - 1.0) > 0.0001 for v in s)

            if is_translated or is_rotated or is_scaled:
                unfrozen.append(node)
        return list(set(unfrozen))

    def check_history(self, nodes):
        """
        [검증] History (히스토리)
        - 노드에 남아있는 히스토리를 검사합니다.

        :param nodes: 검사할 트랜스폼 노드 리스트
        :return: 히스토리가 남아있는 노드 리스트
        :rtype: list
        """
        # pruneDagObjects=True 옵션으로 불필요한 DAG 노드는 제외하고 순수 히스토리만 봅니다.
        return [n for n in nodes if cmds.listHistory(n, pruneDagObjects=True)]

    def check_mesh_errors(self, nodes):
        """
        [검증] 지오메트리 에러
        - Ngons (5각형 이상의 면)
        - Non-manifold (이어지지 않은 구조의 지오메트리)

        :param nodes: 검사할 트랜스폼 노드 리스트
        :return: 에러가 있는 노드 리스트
        :rtype: list
        """
        errors = []
        for node in nodes:
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True, type='mesh') or []
            if not shapes:
                continue
            mesh_node = shapes[0]

            # 1. Ngons 체크: 면의 버텍스가 4개를 초과하는 경우
            cmds.select(mesh_node, r=True)
            cmds.polySelectConstraint(mode=3, type=0x0008, size=3)  # size=3은 N-gons(5각 이상)
            ngons_components = cmds.ls(sl=True)
            cmds.polySelectConstraint(disable=True) # 검사 후에는 항상 비활성화

            # 2. Non-manifold 체크
            non_manifold_vtx = cmds.polyInfo(mesh_node, nonManifoldVertices=True)
            non_manifold_edge = cmds.polyInfo(mesh_node, nonManifoldEdges=True)

            if ngons_components or non_manifold_vtx or non_manifold_edge:
                errors.append(node)

        cmds.select(cl=True)
        return list(set(errors))


    def cleanup_unknown_nodes(self):
        """
        [수정] Unknown 노드 정리
        - 씬에 남아있는 알 수 없는 노드(플러그인 유실 등)를 모두 삭제합니다.
        
        :return: 삭제된 unknown 노드 리스트
        :rtype: list
        """
        unknown = cmds.ls(type='unknown')
        if not unknown:
            return []

        cmds.undoInfo(openChunk=True, chunkName="DeleteUnknownNodes")
        try:
            deleted_nodes = []
            for node in unknown:
                if cmds.objExists(node):
                    cmds.delete(node)
                    deleted_nodes.append(node)
        finally:
            cmds.undoInfo(closeChunk=True)
        return deleted_nodes

    def fix_history_and_transforms(self, nodes):
        """
        [수정] 선택된 노드의 히스토리를 삭제하고 변환 값을 초기화(Freeze)합니다.

        :param nodes: 수정할 트랜스폼 노드 리스트
        """
        if not nodes: return
        cmds.undoInfo(openChunk=True, chunkName="FixHistoryAndTransforms")
        try:
            for node in nodes:
                if not cmds.objExists(node): continue
                # 1. 히스토리 삭제
                cmds.delete(node, constructionHistory=True)
                # 2. 변환 값 초기화 (Freeze Transforms)
                cmds.makeIdentity(node, apply=True, translate=1, rotate=1, scale=1, normal=0)
        finally:
            cmds.undoInfo(closeChunk=True)

    def check_uv_errors(self, nodes):
        """
        [검증] UV 에러
        - UV 셋이 없는 경우
        - UV가 할당되지 않은 페이스가 있는 경우
        
        :param nodes: 검사할 트랜스폼 노드 리스트
        :return: UV 에러가 있는 노드 이름과 에러 내용 리스트
        :rtype: list
        """
        uv_errors = []
        for node in nodes:
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True, type='mesh') or []
            if not shapes: continue
            mesh_node = shapes[0]

            # 1. UV 세트 존재 여부 확인
            uv_sets = cmds.polyUVSet(mesh_node, q=True, allUVSets=True)
            if not uv_sets:
                uv_errors.append(f"{node} (No UV Sets)")
                continue

            # 2. UV가 할당되지 않은 페이스 확인
            unmapped_faces = []
            face_iter = range(cmds.polyEvaluate(mesh_node, f=True))
            for i in face_iter:
                face_name = f'{mesh_node}.f[{i}]'
                uvs = cmds.polyListComponentConversion(face_name, fromFace=True, toUV=True)
                if not uvs:
                    unmapped_faces.append(face_name)
            
            if unmapped_faces:
                uv_errors.append(f"{node} (Unassigned UVs)")

        return list(set(uv_errors))

    def check_multi_uvsets(self, nodes):
        """
        [검증] 다중 UV 셋 및 이름('map1')
        - UV 셋이 2개 이상인 경우
        - UV 셋이 1개지만 이름이 'map1'이 아닌 경우

        :param nodes: 검사할 트랜스폼 노드 리스트
        :return: UV 셋 에러가 있는 노드와 에러 내용 리스트
        :rtype: list
        """
        multi_uv_errors = []
        for node in nodes:
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True, type='mesh') or []
            if not shapes: continue
            mesh_node = shapes[0]

            uv_sets = cmds.polyUVSet(mesh_node, q=True, allUVSets=True) or []

            if len(uv_sets) > 1:
                multi_uv_errors.append(f"{node} (Multiple UV Sets: {len(uv_sets)})")
            elif uv_sets and uv_sets[0] != 'map1':
                multi_uv_errors.append(f"{node} (Wrong UV Set Name: {uv_sets[0]})")

        return list(set(multi_uv_errors))

    def check_uv_overlapping(self, nodes):
        """
        [검증] UV 겹침 (Overlapping)
        - 오브젝트의 모든 페이스를 선택한 후, 그 안에서 UV 겹침을 검사합니다.
        - cmds.polyUVOverlap 명령어를 사용합니다.

        :param nodes: 검사할 트랜스폼 노드 리스트
        :return: UV가 겹치는 오브젝트의 노드 이름과 상세 정보 리스트
        :rtype: list
        """
        nodes_with_overlap = []
        
        # 기존 선택 상태를 저장해두었다가 나중에 복원합니다.
        original_selection = cmds.ls(sl=True) or []

        try:
            # 1. 노드를 하나씩 순회하며 검사합니다.
            for node in nodes:
                # 2. 노드에 해당하는 모든 페이스(face) 컴포넌트 이름을 만듭니다.
                faces = f'{node}.f[*]'
                
                # 페이스 컴포넌트가 실제로 존재하는지 확인합니다. (오브젝트가 없거나, 메쉬가 아닌 경우 등)
                if not cmds.objExists(faces): 
                    continue

                # 3. 해당 오브젝트의 모든 페이스를 선택합니다.
                cmds.select(faces, r=True, noExpand=True) # noExpand는 많은 컴포넌트 선택 시 성능에 도움을 줄 수 있습니다.
                
                # 4. 선택된 페이스들을 대상으로 겹치는 UV가 있는지 확인합니다.
                overlapping_components = cmds.polyUVOverlap(oc=True)
                
                # 5. 겹치는 UV가 발견되었는지 확인합니다.
                if overlapping_components:
                    num_overlapping_uvs = len(overlapping_components)
                    # 결과를 노드 이름과 함께 UI에 친화적인 형태로 추가합니다.
                    nodes_with_overlap.append(f"{node} ({num_overlapping_uvs} overlapping UVs)")

        finally:
            # 6. 검사 후 원래 선택 상태로 복원합니다.
            if original_selection:
                cmds.select(original_selection, r=True)
            else:
                cmds.select(cl=True)
                
        return list(set(nodes_with_overlap))

    def fix_naming_conventions(self, nodes):
        """
        [수정] 네이밍 규칙 수정
        - 노드 이름이 설정된 접미사로 끝나지 않는 경우 접미사를 추가합니다.

        :param nodes: 수정할 트랜스폼 노드 리스트
        """
        if not nodes: return
        cmds.undoInfo(openChunk=True, chunkName="FixNamingConventions")
        try:
            for node in nodes:
                if not cmds.objExists(node): continue
                name_only = node.split('|')[-1]
                if not name_only.endswith(self.mesh_suffix):
                    new_name = name_only + self.mesh_suffix
                    cmds.rename(node, new_name)
                    print(f"Renamed {name_only} to {new_name}")
        finally:
            cmds.undoInfo(closeChunk=True)

    def cleanup_uvsets(self, nodes):
        """
        [수정] 다중 UV 셋 정리
        - 'map1' UV 셋만 남기고 나머지 UV 셋은 삭제합니다.
        - UV 셋이 하나만 있고 이름이 'map1'이 아니면 'map1'으로 변경합니다.

        :param nodes: 수정할 노드 이름 리스트 (에러 메시지 포함 가능)
        """
        if not nodes: return
        cmds.undoInfo(openChunk=True, chunkName="CleanupUVSets")
        try:
            for node_str in nodes:
                # 'node (error message)' 형식일 수 있으므로 노드 이름만 추출합니다.
                clean_node = node_str.split(' (')[0]
                if not cmds.objExists(clean_node): continue

                shapes = cmds.listRelatives(clean_node, shapes=True, fullPath=True, type='mesh') or []
                if not shapes: continue
                mesh = shapes[0]

                uv_sets = cmds.polyUVSet(mesh, q=True, allUVSets=True) or []
                
                if len(uv_sets) > 1:
                    # map1이 있다면 map1을 제외하고 삭제, 없다면 첫번째 것을 map1으로 바꾸고 나머지를 삭제
                    if 'map1' in uv_sets:
                        for uv_set in uv_sets:
                            if uv_set != 'map1':
                                cmds.polyUVSet(mesh, delete=True, uvSet=uv_set)
                    else:
                        # 첫 세트를 map1으로 이름 변경
                        cmds.polyUVSet(mesh, rename=True, newUVSet='map1', uvSet=uv_sets[0])
                        # 나머지 세트 삭제
                        for uv_set in uv_sets[1:]:
                            cmds.polyUVSet(mesh, delete=True, uvSet=uv_set)

                elif uv_sets and uv_sets[0] != 'map1':
                    # UV 셋이 하나지만 이름이 map1이 아닌 경우
                    cmds.polyUVSet(mesh, rename=True, newUVSet='map1', uvSet=uv_sets[0])
            
            print("UV 셋 정리를 완료했습니다.")
        finally:
            cmds.undoInfo(closeChunk=True)