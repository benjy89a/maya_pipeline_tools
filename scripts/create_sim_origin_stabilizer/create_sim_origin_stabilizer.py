import maya.cmds as cmds
import maya.api.OpenMaya as om

def create_sim_origin_stabilizer(loc_name='locator1', sim_target=None):
    """
    [World -> Origin -> World] 시뮬레이션 워크플로우를 위한 리깅 생성기.

    용도:
    1. 월드 좌표의 애니메이션 캐시를 'Origin'으로 이동시켜 안정적으로 시뮬레이션 수행.
    2. 시뮬레이션 완료 후 다시 'World'로 복구하여 최종 캐시 익스포트.

    주의사항:
    - sim_target은 반드시 트랜스폼 값이 0(Frozen)이어야 정확한 위치에 배치됩니다.
    """
    if not cmds.objExists(loc_name):
        cmds.warning(f"기준 로케이터를 찾을 수 없습니다: {loc_name}")
        return

    # 1. 정밀 매트릭스 계산 (OpenMaya 2.0)
    sel = om.MSelectionList()
    sel.add(loc_name)
    dag = sel.getDagPath(0)
    
    world_m = dag.inclusiveMatrix()
    inv_m = world_m.inverse()

    # 2. 메인 그룹 생성 (matrix_rig_grp)
    rig_grp = cmds.createNode("transform", name="matrix_rig_grp")
    
    # 복귀를 위한 원래 월드 값 보존
    cmds.addAttr(rig_grp, ln="originalWorldMatrix", dt="matrix")
    cmds.setAttr(f"{rig_grp}.originalWorldMatrix", list(world_m), type="matrix")

    # 3. 원점으로 이동 (Inverse Matrix 적용)
    cmds.xform(rig_grp, m=list(inv_m), ws=True)

    # 4. 공간 전환 스위치 설정
    attr_full = f"{rig_grp}.sim_space"
    cmds.addAttr(rig_grp, ln="sim_space", at="enum", en="World:Origin:", k=True)

    # SDK: Origin 모드 (1) - 원점 위치
    cmds.setDrivenKeyframe([f"{rig_grp}.t", f"{rig_grp}.r"], cd=attr_full, dv=1)

    # SDK: World 모드 (0) - 월드 복귀
    cmds.setAttr(f"{rig_grp}.t", 0, 0, 0)
    cmds.setAttr(f"{rig_grp}.r", 0, 0, 0)
    cmds.setDrivenKeyframe([f"{rig_grp}.t", f"{rig_grp}.r"], cd=attr_full, dv=0)

    # 5. 타겟 확인 및 경고
    if sim_target and cmds.objExists(sim_target):
        t_val = cmds.getAttr(f"{sim_target}.t")[0]
        if any(t_val):
            cmds.warning(f"'{sim_target}'의 트랜스폼 값이 0이 아닙니다. 오프셋이 발생할 수 있습니다.")

    cmds.setAttr(attr_full, 1) # 기본값을 Origin으로 설정
    print(f"[완료] 시뮬레이션 안정화 리그 생성: {rig_grp}")
    
    return rig_grp

# 실행
# create_sim_origin_stabilizer(loc_name='locator1', sim_target='leeminhoGreymtmblue')