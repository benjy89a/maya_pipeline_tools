import maya.cmds as cmds
import json
import os

def export_shader_map_to_json(file_name="shader_map_data.json"):
    """
    선택된 지오메트리의 쉐이더 정보를 '현재 씬 파일'과 같은 위치에 JSON으로 저장합니다.
    """
    # 1. 저장 경로 설정 (현재 씬 파일 기준)
    scene_path = cmds.file(query=True, sceneName=True)
    
    if not scene_path:
        # 씬이 저장되지 않은 상태라면 워크스페이스나 현재 작업 디렉토리 활용
        save_dir = cmds.workspace(query=True, directory=True) or os.getcwd()
        print("⚠️ 주의: 씬이 저장되지 않아 기본 경로에 저장합니다.")
    else:
        save_dir = os.path.dirname(scene_path)

    json_path = os.path.join(save_dir, file_name)

    # 2. 선택된 트랜스폼 노드 가져오기
    selection = cmds.ls(selection=True, type='transform')
    if not selection:
        print("❌ 오류: 지오메트리 트랜스폼 노드를 선택해야 합니다.")
        return

    shader_mapping_dict = {}

    for node_path in selection:
        # 네임스페이스 제거한 짧은 이름 (JSON Key)
        short_name_with_ns = node_path.split('|')[-1]
        object_key = short_name_with_ns.split(':')[-1]

        shader_info_list = []

        # 유효한 쉐이프 노드 추출 (Intermediate 제외)
        all_shapes = cmds.listRelatives(node_path, shapes=True, fullPath=True) or []
        shapes = [s for s in all_shapes if not cmds.getAttr(f"{s}.intermediateObject")]

        for shape_node in shapes:
            short_shape_name = shape_node.split('|')[-1].split(':')[-1]

            # 쉐이프에 연결된 SG 탐색 (사용자 제공 로직 반영)
            connected_sgs = cmds.listConnections(shape_node, type='shadingEngine', destination=True, source=False)
            if not connected_sgs: continue
            
            connected_sgs = sorted(list(set(connected_sgs)))

            for full_sg_name in connected_sgs:
                sg_name = full_sg_name.split(':')[-1]

                # [핵심] SG 멤버십 쿼리를 통한 페이스 단위 추출
                sg_members = cmds.sets(full_sg_name, query=True)
                filtered_members = []

                if sg_members:
                    for member in sg_members:
                        base_member_name = member.split('|')[-1]

                        # A. 컴포넌트인 경우 (.f[n])
                        if '.' in base_member_name:
                            component_base = base_member_name.split('.')[0]
                            if component_base == object_key or component_base == short_shape_name:
                                component_part = base_member_name.split('.', 1)[1]
                                filtered_members.append(f"{short_shape_name}.{component_part}")
                        
                        # B. 오브젝트 전체인 경우
                        elif base_member_name == object_key or base_member_name == short_shape_name:
                            filtered_members.append(short_shape_name)

                if filtered_members:
                    shader_info_list.append({
                        "sg_name": sg_name,
                        "members": sorted(list(set(filtered_members)))
                    })

        if shader_info_list:
            shader_mapping_dict[object_key] = shader_info_list

    # 3. JSON 파일 저장
    try:
        with open(json_path, 'w') as f:
            json.dump(shader_mapping_dict, f, indent=4)
        print(f"✅ JSON 매핑 파일 생성 완료 (씬 경로): {json_path}")
    except Exception as e:
        print(f"❌ 파일 저장 오류: {e}")

def restore_shaders_from_json(map_root_directory):
    """
    지정된 폴더에서 레퍼런스 이름과 일치하는 JSON을 찾아 복구합니다.
    """
    all_refs = cmds.ls(type='reference')
    for ref_node in all_refs:
        if 'sharedReferenceNode' in ref_node: continue
        
        try:
            ref_path = cmds.referenceQuery(ref_node, filename=True)
            ref_ns = cmds.referenceQuery(ref_node, namespace=True)
            if not ref_ns: continue

            asset_base = os.path.splitext(os.path.basename(ref_path))[0]
            json_path = os.path.join(map_root_directory, f"{asset_base}.json")

            if not os.path.exists(json_path): continue

            with open(json_path, 'r') as f:
                shader_map = json.load(f)

            for transform_short, info_list in shader_map.items():
                ns_prefix = f"{ref_ns}:"
                for info in info_list:
                    full_sg = f"{ns_prefix}{info['sg_name']}"
                    if not cmds.objExists(full_sg): continue
                    
                    for member in info['members']:
                        if "." in member:
                            shape_part, comp_part = member.split('.', 1)
                            full_member = f"{ns_prefix}{shape_part}.{comp_part}"
                        else:
                            full_member = f"{ns_prefix}{member}"

                        if cmds.objExists(full_member):
                            cmds.sets(full_member, edit=True, forceElement=full_sg)
            
            print(f"✅ 복구 완료: {ref_ns}")
        except Exception as e:
            print(f"⚠️ 오류 ({ref_node}): {e}")

# 실행 예시
# export_shader_map_to_json("my_shader_data.json")
