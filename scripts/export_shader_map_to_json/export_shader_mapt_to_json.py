import maya.cmds as cmds
import json
import os

def export_shader_map_to_json(file_name="shader_map_data.json"):
    """
    선택된 지오메트리에 할당된 쉐이더 정보를 JSON 파일로 저장합니다.

    [주요 기능]
    - 오브젝트 단위, 페이스 단위의 쉐이더 할당 정보를 모두 추출합니다.
    - 네임스페이스를 제거하여 레퍼런스 환경에서도 동일한 키를 유지합니다.
    - JSON 파일은 현재 Maya 씬 파일과 동일한 경로에 생성됩니다.

    [사용법]
    1. 쉐이더 정보를 추출할 지오메트리(트랜스폼 노드)를 선택합니다.
    2. export_shader_map_to_json("my_asset_shaders.json") 형식으로 실행합니다.
       파일명을 생략하면 "shader_map_data.json"으로 저장됩니다.
    """
    scene_path = cmds.file(query=True, sceneName=True)
    if not scene_path:
        save_dir = cmds.workspace(query=True, directory=True)
        cmds.warning("씬 파일이 저장되지 않았습니다. 워크스페이스 경로에 저장합니다: {}".format(save_dir))
    else:
        save_dir = os.path.dirname(scene_path)

    json_path = os.path.join(save_dir, file_name)

    selection = cmds.ls(selection=True, type='transform')
    if not selection:
        cmds.error("지오메트리 트랜스폼 노드를 하나 이상 선택해야 합니다.")
        return

    shader_mapping_dict = {}
    print("선택된 오브젝트로부터 쉐이더 정보 추출을 시작합니다...")

    for node_path in selection:
        short_name_with_ns = node_path.split('|')[-1]
        object_key = short_name_with_ns.split(':')[-1]

        shader_info_list = []

        all_shapes = cmds.listRelatives(node_path, shapes=True, fullPath=True) or []
        shapes = [s for s in all_shapes if not cmds.getAttr("{}.intermediateObject".format(s))]

        if not shapes:
            print("경고: '{}'에서 유효한 쉐이프 노드를 찾을 수 없습니다.".format(node_path))
            continue

        for shape_node in shapes:
            short_shape_name = shape_node.split('|')[-1].split(':')[-1]

            connected_sgs = cmds.listConnections(shape_node, type='shadingEngine', destination=True, source=False)
            if not connected_sgs:
                continue
            
            connected_sgs = sorted(list(set(connected_sgs)))

            for full_sg_name in connected_sgs:
                sg_name = full_sg_name.split(':')[-1]

                sg_members = cmds.sets(full_sg_name, query=True)
                if not sg_members:
                    continue

                filtered_members = []
                for member in sg_members:
                    base_member_name = member.split('|')[-1].split(':')[-1]

                    if '.' in base_member_name:
                        component_base = base_member_name.split('.')[0]
                        if component_base == object_key or component_base == short_shape_name:
                            component_part = base_member_name.split('.', 1)[1]
                            filtered_members.append("{}.{}".format(short_shape_name, component_part))
                    
                    elif base_member_name == object_key or base_member_name == short_shape_name:
                        filtered_members.append(short_shape_name)

                if filtered_members:
                    shader_info_list.append({
                        "sg_name": sg_name,
                        "members": sorted(list(set(filtered_members)))
                    })

        if shader_info_list:
            shader_mapping_dict[object_key] = shader_info_list
            print(" > '{}'의 쉐이더 정보 처리 완료.".format(object_key))

    if not shader_mapping_dict:
        cmds.warning("추출할 쉐이더 정보가 없습니다.")
        return

    try:
        with open(json_path, 'w') as f:
            json.dump(shader_mapping_dict, f, indent=4, ensure_ascii=False)
        
        print("="*50)
        print("✅ JSON 쉐이더 맵 파일 생성이 완료되었습니다.")
        print("   위치: {}".format(json_path))
        print("="*50)

    except Exception as e:
        cmds.error("파일 저장 중 오류 발생: {}".format(e))