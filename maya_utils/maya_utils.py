from functools import partial
import maya.cmds as cmds

def get_all_mesh_transforms():
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

def delete_unknown_nodes():
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
            # 노드가 존재하고, 잠겨있지 않은 경우에만 삭제 시도
            if cmds.objExists(node) and not cmds.lockNode(node, query=True)[0]:
                try:
                    cmds.delete(node)
                    deleted_nodes.append(node)
                except Exception as e:
                    print(f"알 수 없는 노드 삭제 실패 '{node}': {e}")
            elif cmds.objExists(node):
                 print(f"잠긴(locked) 노드는 건너뜁니다: {node}")
    finally:
        cmds.undoInfo(closeChunk=True)
    return deleted_nodes

def fix_history_and_transforms(nodes):
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

def list_scripts_jobs():
    for job in cmds.scriptJob(listJobs=True):
        print(job.replace('\n',''))
    
def remove_script_job(name):
    for job in cmds.scriptJob(listJobs=True):
        buf = job.split(':')
        if name in job:
            cmds.evalDeferred(partial(cmds.scriptJob, kill=int(buf[0]), force=True),lowestPriority=True)
