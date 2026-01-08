# -*- coding: utf-8 -*-
import maya.cmds as cmds
import os
import importlib

# 공통 유틸리티 모듈 임포트
from core import core_utils as core_utils
from core import log as core_log # 새로 만든 로그 모듈 임포트
from maya_utils import maya_utils
importlib.reload(core_utils)
importlib.reload(core_log) # 로그 모듈도 리로드
importlib.reload(maya_utils)

# --- 로거 설정 ---
# 로그 파일 경로를 현재 스크립트 위치 기준으로 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_dir, 'scene_validation.log')

# 중앙 로깅 함수를 호출하여 로거 인스턴스 가져오기
log = core_log.get_logger(__name__, log_file_path)
log.info("--- Validator Loded: New Session ---")
# --- 로거 설정 끝 ---


class SceneValidatorCore:
    """
    모델링 데이터 검증을 위한 핵심 로직을 담고 있는 클래스입니다.
    """
    def __init__(self):
        """
        SceneValidatorCore 클래스의 생성자입니다.
        'naming_convention.config' 설정 파일을 읽어 검증 규칙을 초기화합니다.
        """
        # 클래스 내에서는 모듈 레벨의 로거와 로그 파일 경로를 사용합니다.
        self.log = log
        self.log_file_path = log_file_path
        
        self.log.info("SceneValidatorCore 인스턴스를 생성합니다.")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'naming_convention.config')

        self.mesh_suffix = core_utils.get_config_value(
            config_path, 'naming_convention', 'mesh_suffix', fallback='_geo'
        )
        
        if self.mesh_suffix == '_geo' and not os.path.exists(config_path):
             self.log.warning(f"설정 파일을 찾을 수 없습니다: {config_path}. 기본 접미사 '{self.mesh_suffix}'를 사용합니다.")

        self.log.info("초기화 완료. 메쉬 접미사: '%s'", self.mesh_suffix)


    def get_all_mesh_transforms(self):
        """
        씬에 있는 모든 메쉬의 트랜스폼 노드를 수집합니다.
        """
        return maya_utils.get_all_mesh_transforms()

    def check_naming_conventions(self, nodes):
        """
        [검증] 네이밍 규칙
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
        """
        unfrozen = []
        for node in nodes:
            t = cmds.getAttr(f"{node}.translate")[0]
            r = cmds.getAttr(f"{node}.rotate")[0]
            s = cmds.getAttr(f"{node}.scale")[0]

            is_translated = any(abs(v) > 0.0001 for v in t)
            is_rotated = any(abs(v) > 0.0001 for v in r)
            is_scaled = any(abs(v - 1.0) > 0.0001 for v in s)

            if is_translated or is_rotated or is_scaled:
                unfrozen.append(node)
        return list(set(unfrozen))

    def check_history(self, nodes):
        """
        [검증] History (히스토리)
        """
        return [n for n in nodes if cmds.listHistory(n, pruneDagObjects=True)]

    def check_mesh_errors(self, nodes):
        """
        [검증] 지오메트리 에러 (Ngons, Non-manifold)
        """
        errors = []
        for node in nodes:
            # ... (내부 로직은 기존과 동일)
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True, type='mesh') or []
            if not shapes: continue
            mesh_node = shapes[0]

            cmds.select(mesh_node, r=True)
            cmds.polySelectConstraint(mode=3, type=0x0008, size=3)
            ngons_components = cmds.ls(sl=True)
            cmds.polySelectConstraint(disable=True)

            non_manifold_vtx = cmds.polyInfo(mesh_node, nonManifoldVertices=True)
            non_manifold_edge = cmds.polyInfo(mesh_node, nonManifoldEdges=True)

            if ngons_components or non_manifold_vtx or non_manifold_edge:
                errors.append(node)

        cmds.select(cl=True)
        return list(set(errors))

    def cleanup_unknown_nodes(self):
        """
        [수정] Unknown 노드 정리
        """
        self.log.info("Unknown 노드 정리를 시작합니다...")
        deleted_nodes = maya_utils.delete_unknown_nodes()
        if deleted_nodes:
            self.log.info("%d개의 Unknown 노드를 삭제했습니다.", len(deleted_nodes))
            self.log.debug("삭제된 노드 목록: %s", deleted_nodes)
        else:
            self.log.info("삭제할 Unknown 노드가 없습니다.")
        return deleted_nodes

    def fix_history_and_transforms(self, nodes):
        """
        [수정] 선택된 노드의 히스토리를 삭제하고 변환 값을 초기화(Freeze)합니다.
        """
        self.log.info("히스토리 삭제 및 Freeze Transform을 %d개 노드에 대해 시작합니다.", len(nodes))
        result = maya_utils.fix_history_and_transforms(nodes)
        self.log.info("히스토리 및 Transform 수정 완료.")
        return result

    def check_uv_errors(self, nodes):
        """
        [검증] UV 에러 (UV 셋 부재, 할당되지 않은 UV)
        """
        uv_errors = []
        for node in nodes:
            # ... (내부 로직은 기존과 동일)
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True, type='mesh') or []
            if not shapes: continue
            mesh_node = shapes[0]

            uv_sets = cmds.polyUVSet(mesh_node, q=True, allUVSets=True)
            if not uv_sets:
                uv_errors.append(f"{node} (No UV Sets)")
                continue

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
        """
        multi_uv_errors = []
        for node in nodes:
            # ... (내부 로직은 기존과 동일)
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
        """
        nodes_with_overlap = []
        original_selection = cmds.ls(sl=True) or []

        try:
            for node in nodes:
                faces = f'{node}.f[*]'
                if not cmds.objExists(faces): continue

                cmds.select(faces, r=True, noExpand=True)
                overlapping_components = cmds.polyUVOverlap(oc=True)
                
                if overlapping_components:
                    num_overlapping_uvs = len(overlapping_components)
                    nodes_with_overlap.append(f"{node} ({num_overlapping_uvs} overlapping UVs)")

        finally:
            if original_selection:
                cmds.select(original_selection, r=True)
            else:
                cmds.select(cl=True)
                
        return list(set(nodes_with_overlap))

    def fix_naming_conventions(self, nodes):
        """
        [수정] 네이밍 규칙 수정
        """
        self.log.info("네이밍 규칙 수정을 시작합니다...")
        if not nodes:
            self.log.info("수정할 노드가 없습니다.")
            return

        cmds.undoInfo(openChunk=True, chunkName="FixNamingConventions")
        try:
            for node in nodes:
                if not cmds.objExists(node):
                    self.log.warning("'%s' 노드가 씬에 존재하지 않아 건너뜁니다.", node)
                    continue
                name_only = node.split('|')[-1]
                if not name_only.endswith(self.mesh_suffix):
                    new_name = name_only + self.mesh_suffix
                    cmds.rename(node, new_name)
                    self.log.info("이름 변경: '%s' -> '%s'", name_only, new_name)
        finally:
            cmds.undoInfo(closeChunk=True)
        self.log.info("네이밍 규칙 수정을 완료했습니다.")

    def cleanup_uvsets(self, nodes):
        """
        [수정] 다중 UV 셋 정리
        """
        self.log.info("UV 셋 정리를 시작합니다...")
        if not nodes:
            self.log.info("정리할 UV 셋이 있는 노드가 없습니다.")
            return
            
        cmds.undoInfo(openChunk=True, chunkName="CleanupUVSets")
        try:
            for node_str in nodes:
                clean_node = node_str.split(' (')[0]
                if not cmds.objExists(clean_node):
                    self.log.warning("'%s' 노드가 씬에 존재하지 않아 건너뜁니다.", clean_node)
                    continue

                shapes = cmds.listRelatives(clean_node, shapes=True, fullPath=True, type='mesh') or []
                if not shapes: continue
                mesh = shapes[0]

                uv_sets = cmds.polyUVSet(mesh, q=True, allUVSets=True) or []
                
                if len(uv_sets) > 1:
                    self.log.debug("'%s' 노드의 다중 UV 셋을 정리합니다.", clean_node)
                    if 'map1' in uv_sets:
                        for uv_set in uv_sets:
                            if uv_set != 'map1':
                                cmds.polyUVSet(mesh, delete=True, uvSet=uv_set)
                                self.log.debug(" - '%s' 에서 '%s' UV 셋 삭제", clean_node, uv_set)
                    else:
                        cmds.polyUVSet(mesh, rename=True, newUVSet='map1', uvSet=uv_sets[0])
                        self.log.debug(" - '%s' 에서 '%s' -> 'map1' 이름 변경", clean_node, uv_sets[0])
                        for uv_set in uv_sets[1:]:
                            cmds.polyUVSet(mesh, delete=True, uvSet=uv_set)
                            self.log.debug(" - '%s' 에서 '%s' UV 셋 삭제", clean_node, uv_set)

                elif uv_sets and uv_sets[0] != 'map1':
                    self.log.debug("'%s' 노드의 UV 셋 이름을 'map1'으로 변경합니다.", clean_node)
                    cmds.polyUVSet(mesh, rename=True, newUVSet='map1', uvSet=uv_sets[0])
            
            self.log.info("UV 셋 정리를 완료했습니다.")
        finally:
            cmds.undoInfo(closeChunk=True)
