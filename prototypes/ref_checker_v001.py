"""
prototypes.ref_checker_v001의 Docstring
디벨롭 예정 사항:
1. 씬 내 다수의 레퍼런스 파일 일괄 검수 기능 추가
2. 동일 어셋(동일 경로)을 참조하는 다수의 레퍼런스 노드에 처리기능 추가 예정
"""

from pathlib import Path
import maya.cmds as cmds
import re

# 1. 현재 선택된 혹은 첫 번째 레퍼런스 파일 경로 가져오기
# (참고: [0]은 첫 번째 레퍼런스를 가져옵니다. 필요에 따라 반복문으로 돌릴 수 있습니다.)
all_refs = cmds.file(q=True, r=True)
if not all_refs:
    cmds.error("씬에 레퍼런스 파일이 없습니다.")

file_path = Path(all_refs[0])
ref_namespace = cmds.referenceQuery(str(file_path), namespace=True, shortName=True)

# 2. 부모 폴더 경로 및 마야 파일(.ma) 리스트업
folder_path = file_path.parent
maya_files = list(folder_path.glob('*.ma'))

# 3. 버전 추출 규칙 정의
# assetName_rig_v(\d+) : 파일명 중간에 _v로 시작하는 숫자를 찾음
version_pattern = r'_v(\d+)'

# 4. 현재 파일의 버전 숫자 추출
current_match = re.search(version_pattern, file_path.name)
if current_match:
    current_version_num = int(current_match.group(1))
else:
    current_version_num = -1
    print(f"경고: 현재 파일({file_path.name})에서 버전 형식을 찾을 수 없습니다.")

# 5. 폴더 내 파일들을 전수 조사하여 최신 버전 찾기
latest_version_num = -1
latest_file_path = None

for f in maya_files:
    # 각 파일명에서 버전 숫자 추출
    match = re.search(version_pattern, f.name)
    if match:
        version_num = int(match.group(1))
        
        # 현재까지 찾은 숫자보다 크면 업데이트
        if version_num > latest_version_num:
            latest_version_num = version_num
            latest_file_path = f

# 6. 결과 비교 및 출력
print("-" * 50)
print(f"네임스페이스: {ref_namespace}")
print(f"현재 경로: {file_path.name} (v{current_version_num:03d})")

if latest_file_path:
    print(f"최신 경로: {latest_file_path.name} (v{latest_version_num:03d})")
    
    if current_version_num < latest_version_num:
        print(f">>> [결과] 업데이트가 필요합니다! (최신: v{latest_version_num:03d})")
    else:
        print(">>> [결과] 현재 최신 버전을 사용 중입니다.")
else:
    print(">>> [결과] 폴더 내에서 유효한 버전 파일을 찾을 수 없습니다.")
print("-" * 50)