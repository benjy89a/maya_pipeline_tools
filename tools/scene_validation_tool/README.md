# 씬 검수 툴 (Scene Validation Tool)
> Maya 씬의 모델링 데이터 무결성을 검증하고 주요 문제들을 자동으로 수정하는 파이프라인 툴입니다.

## 🎥 Demo
![Demo GIF](https://example.com/path/to/your_scene_validation_tool_demo.gif)
*(데모 GIF/이미지를 이곳에 삽입하세요)*

## ✨ 주요 기능 및 검사 항목

### 통합된 워크플로우
- **직관적인 UI**: 검사 결과를 '문제 항목'과 '진행 내역'으로 분리하여 명확한 피드백을 제공합니다.
- **선택적/일괄 수정**: 발견된 문제를 개별적으로 선택하여 수정하거나, 자동 수정 가능한 모든 항목을 한 번에 해결할 수 있습니다.
- **로그 파일**: 모든 검사 및 수정 내역을 로그 파일(`scene_validation.log`)에 기록하여 추적 및 디버깅을 지원합니다.

### 검사 항목 상세
- **씬(Scene)**
    - **Unknown 노드**: 씬에 남은 불필요한 Unknown 노드를 검사하고 삭제합니다.
- **네이밍(Naming)**
    - **네이밍 규칙**: `naming_convention.config` 파일에 정의된 접미사(`_geo` 등) 규칙 준수 여부를 검사하고 수정합니다.
- **트랜스폼 및 히스토리(Transform & History)**
    - **Freeze Transforms**: 오브젝트의 Transform(Translate, Rotate, Scale) 값이 초기화되었는지 검사하고 수정합니다.
    - **History**: 지오메트리에 남아있는 히스토리를 검사하고 삭제합니다.
- **지오메트리(Geometry)**
    - **Ngons**: 5각형 이상의 폴리곤(N-gons)을 검사합니다.
    - **Non-manifold**: 비-다양체(Non-manifold) 지오메트리를 검사합니다.
- **UV**
    - **UV 할당**: UV가 할당되지 않은 면(Unassigned UVs) 또는 UV 셋이 없는(No UV Sets) 오브젝트를 검사합니다.
    - **UV 세트 이름/개수**: UV 셋이 2개 이상이거나, 이름이 'map1'이 아닌 경우를 검사하고 'map1'만 남도록 정리합니다.
    - **UV 겹침(Overlapping)**: UV가 겹치는 부분을 검사합니다.

## 🛠 기술 스택
- Python 3
- PySide2 (UI)
- Maya API (`maya.cmds`)

## 🚀 설치 및 사용법

이 툴은 **Python 3를 지원하는 Maya (2022 이상 권장)** 에서 실행됩니다.

1.  **설치**: `maya_pipeline_tools` 폴더를 Maya 스크립트 경로에 추가합니다. (`userSetup.py` 사용 권장)

2.  **실행 (UI)**: Maya 스크립트 에디터에서 다음 코드를 실행합니다.
    ```python
    from tools.scene_validation_tool import scene_valiation_tool_ui
    import importlib
    importlib.reload(scene_valiation_tool_ui)
    
    scene_valiation_tool_ui.main()
    ```

3.  **실행 (Core API)**: UI 없이 핵심 검증 로직만 사용할 수도 있습니다.
    ```python
    from tools.scene_validation_tool import scene_validation_tool
    import importlib
    importlib.reload(scene_validation_tool)

    from tools.scene_validation_tool.scene_validation_tool import SceneValidatorCore

    # 1. 검증기 인스턴스 생성
    validator = SceneValidatorCore()

    # 2. 씬의 모든 메쉬 가져오기
    all_meshes = validator.get_all_mesh_transforms()
    print(f"검사 대상 메쉬: {len(all_meshes)}개")

    # 3. 특정 항목 검사 실행 (예: 트랜스폼)
    unfrozen_nodes = validator.check_freeze_transforms(all_meshes)
    if unfrozen_nodes:
        print(f"[문제 발견] {len(unfrozen_nodes)}개의 노드에 Freeze가 필요합니다: {unfrozen_nodes}")
        
        # 4. 자동 수정 실행
        validator.fix_history_and_transforms(unfrozen_nodes)
        print("수정이 완료되었습니다.")
    else:
        print("[성공] 모든 노드의 트랜스폼이 Freeze 상태입니다.")
    ```

## 🧠 문제 해결 및 설계
- **모듈화**: UI 로직(`scene_valiation_tool_ui.py`)과 핵심 검증 로직(`scene_validation_tool.py`)을 분리하여 코드의 재사용성 및 유지보수성을 높였습니다.
- **사용자 경험(UX)**: 여러 개별 스크립트로 흩어져 있던 기능을 단일 UI로 통합하고, 검사/수정 워크플로우를 일원화하여 사용 편의성을 개선했습니다.
- **정확성**: `cmds.polyUVOverlap`의 동작 특성을 고려하여 각 오브젝트의 모든 페이스를 선택 후 검사하도록 구현, UV 겹침 검사의 신뢰도를 확보했습니다.

## ⚙️ 설정
툴의 일부 동작은 `naming_convention.config` 파일을 통해 제어할 수 있습니다.

```ini
[naming_convention]
# 메쉬 트랜스폼 노드의 이름이 이 접미사로 끝나야 합니다.
mesh_suffix = _geo
```