import maya.cmds as cmds
import json
import os

def import_shaders_from_json(map_root_directory):
    """
    지정된 폴더에서 레퍼런스 에셋 이름과 일치하는 JSON을 찾아 쉐이더를 가져옵니다.

    [주요 기능]
    - 현재 씬의 모든 레퍼런스를 순회합니다.
    - 레퍼런스 파일명과 동일한 이름의 JSON 파일을 지정된 폴더에서 찾습니다.
    - JSON 파일의 정보를 기반으로 쉐이더(SG)를 다시 할당합니다.
      (오브젝트 단위, 페이스 단위 할당 모두 지원)

    [사용법]
    1. 쉐이더 맵 JSON 파일들이 저장된 폴더 경로를 인자로 전달하여 함수를 실행합니다.
    2. 예: import_shaders_from_json("C:/my_project/assets/char/shader_maps")
    """
    print("쉐이더 가져오기를 시작합니다. 대상 폴더: {}".format(map_root_directory))
    
    all_refs = cmds.ls(type='reference')
    if not all_refs:
        cmds.warning("씬에 레퍼런스 노드가 없습니다.")
        return

    imported_count = 0
    for ref_node in all_refs:
        # sharedReferenceNode는 실제 에셋 레퍼런스가 아니므로 건너뜁니다.
        if 'sharedReferenceNode' in ref_node or '_UNKNOWN_REF_NODE_' in ref_node:
            continue
        
        try:
            # 레퍼런스 파일 경로와 네임스페이스를 가져옵니다.
            ref_path = cmds.referenceQuery(ref_node, filename=True, withoutCopyNumber=True)
            ref_ns = cmds.referenceQuery(ref_node, namespace=True)
            
            if not ref_ns or not ref_ns.startswith(':'):
                continue
            ref_ns = ref_ns[1:]

            # 레퍼런스 파일명(확장자 제외)을 기반으로 JSON 파일 경로를 조합합니다.
            asset_base_name = os.path.splitext(os.path.basename(ref_path))[0]
            json_path = os.path.join(map_root_directory, "{}.json".format(asset_base_name))

            if not os.path.exists(json_path):
                continue

            print(" > '{}' 에셋의 쉐이더 할당을 진행합니다... (네임스페이스: {})".format(asset_base_name, ref_ns))
            
            with open(json_path, 'r') as f:
                shader_map = json.load(f)

            # JSON 데이터를 기반으로 쉐이더를 할당합니다.
            for transform_short, info_list in shader_map.items():
                ns_prefix = "{}:".format(ref_ns)
                
                for info in info_list:
                    full_sg = "{}{}".format(ns_prefix, info['sg_name'])
                    if not cmds.objExists(full_sg):
                        cmds.warning("'{}' Shading Group을 찾을 수 없어 건너뜁니다.".format(full_sg))
                        continue
                    
                    for member in info['members']:
                        full_member_path = "{}{}".format(ns_prefix, member)

                        if cmds.objExists(full_member_path):
                            cmds.sets(full_member_path, edit=True, forceElement=full_sg)
                        else:
                            cmds.warning("'{}' 멤버를 찾을 수 없어 건너뜁니다.".format(full_member_path))
            
            print("   - '{}' 할당 완료.".format(asset_base_name))
            imported_count += 1

        except Exception as e:
            cmds.warning(" '{}' 노드 처리 중 오류 발생: {}".format(ref_node, e))
        
    print("="*50)
    if imported_count > 0:
        print("✅ 총 {}개의 레퍼런스 에셋에 대한 쉐이더 할당을 완료했습니다.".format(imported_count))
    else:
        print("ℹ️ 할당할 쉐이더 정보가 있는 에셋을 찾지 못했습니다.")
    print("="*50)