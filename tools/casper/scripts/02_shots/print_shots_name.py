"""
========================================================
print_shots_name.py
========================================================

[기능]
- 현재 열려있는 Maya 씬 파일의 전체 경로를 스크립트 에디터에 출력합니다.
- 씬이 아직 저장되지 않은 경우, 'Untitled' 상태임을 알려줍니다.

[실행 방법]
- 스크립트를 실행하면 즉시 현재 씬의 경로가 출력됩니다.
"""
import pymel.core as pm

def print_maya_scene_path():
    """
    현재 활성화된 마야 씬 파일의 전체 경로를 출력합니다.
    """
    # 현재 씬 파일의 경로를 가져옵니다.
    scene_path = pm.sceneName()
    
    if not scene_path:
        print("현재 씬이 저장되지 않았습니다. (Untitled)")
    else:
        print(f"현재 마야 씬 경로: {scene_path}")

# 함수 실행
print_maya_scene_path()
