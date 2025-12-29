# 씬 검수 툴 (Scene Validation Tool)

> Maya 씬의 모델링 데이터를 검증하고 수정하는 파이프라인 자동화 툴

## 🎥 Demo
![Demo GIF](https://example.com/path/to/your_scene_validation_tool_demo.gif)
_(_이곳에 툴의 작동 모습을 담은 GIF 또는 이미지 링크를 넣어주세요.)_

## ✨ Features
### UI 및 사용자 경험 개선
-   **직관적인 결과 피드백:** 검사 결과를 '문제 항목' (Failed Items)과 '검사 진행 내역' (Validation Log) 두 개의 패널로 분리하여 어떤 검사가 통과했고 어떤 문제가 발견되었는지 한눈에 파악할 수 있습니다.
-   **통합된 검사 및 수정 워크플로우:** '알 수 없는 노드 삭제', 'UV 세트 정리' 등 기존에 별도의 버튼으로 존재하던 기능들을 메인 검사 리스트에 통합하여 일관된 사용 흐름을 제공합니다.
-   **'선택 항목 수정' 및 '전체 수정' 기능:** 발견된 문제를 사용자가 선택적으로 수정하거나, 자동 수정 가능한 모든 문제를 한 번에 해결할 수 있습니다.

### 지오메트리 및 트랜스폼 검사
-   **네이밍 규칙**: 그룹 이름이 `naming_convention.config` 파일에 지정된 접미사(`_geo` 등)로 끝나는지 검사하고 필요시 수정합니다.
-   **Freeze Transforms**: Translate, Rotate, Scale 값이 초기화되었는지 검사하고 필요시 수정합니다.
-   **History**: 지오메트리에 남아있는 히스토리를 검사하고 필요시 삭제합니다.
-   **지오메트리 에러**:
    -   **Ngons**: 5각형 이상의 면이 있는지 검사합니다.
    -   **Non-manifold**: 비-다양체(Non-manifold) 구조의 지오메트리가 있는지 검사합니다.

### UV 관련 검사
-   **UV 에러**:
    -   **No UV Sets**: UV 셋이 아예 없는 지오메트리를 검사합니다.
    -   **Unassigned UVs**: UV가 할당되지 않은 면이 있는지 검사합니다.
-   **다중 UV 셋 / 잘못된 이름**:
    -   UV 셋이 2개 이상 존재하는 경우를 검사하고 필요시 'map1'만 남기고 정리합니다.
    -   UV 셋이 1개지만, 이름이 `map1`이 아닌 경우를 검사하고 필요시 `map1`으로 변경합니다.
-   **UV 겹침 (Overlapping)**: 각 오브젝트의 모든 페이스를 검사하여 UV 겹침이 있는지 확인하고, 겹치는 UV 개수와 함께 해당 오브젝트의 이름을 보고합니다.

### 씬 전반 검사
-   **Unknown 노드**: 씬에 남아있는 출처를 알 수 없는(Unknown) 노드를 검사하고 필요시 삭제할 수 있습니다.

## 🛠 Tech Stack
-   Python 3
-   PySide2 (UI 구성)
-   Maya API (`maya.cmds`)

## 🚀 Setup & Usage
이 툴은 **Python 3 환경을 지원하는 Maya (Maya 2022 이상 권장)** 에서 실행됩니다.

1.  **설치 방법:**
    *   `maya_pipeline_tools` 폴더를 Maya의 스크립트 경로(`MAYA_SCRIPT_PATH`) 또는 Python 경로(`PYTHONPATH`)에 추가합니다. `userSetup.py`를 사용하여 경로를 등록하는 것을 권장합니다.

2.  **실행 코드 (Maya 스크립트 에디터 또는 Python 셸에서 실행):**
    ```python
    import scripts.scene_validation_tool.scene_valiation_tool_ui as svt_ui
    svt_ui.main()
    ```
    또는 코어 클래스만 사용하여 검증 로직을 직접 실행할 수도 있습니다.
    ```python
    from importlib import reload

    # 코어 클래스 임포트 및 리로드
    import scripts.scene_validation_tool.scene_validation_tool as svt_core_module
    reload(svt_core_module)

    from scripts.scene_validation_tool.scene_validation_tool import SceneValidatorCore

    # 1. 검증기 인스턴스 생성
    validator = SceneValidatorCore()

    # 2. 씬에 있는 모든 메쉬 가져오기
    all_meshes = validator.get_all_mesh_transforms()
    print(f"검사 대상 메쉬: {len(all_meshes)}개")

    # 3. 특정 항목 검사 실행 (예: Freeze Transform)
    unfrozen_nodes = validator.check_freeze_transforms(all_meshes)
    if unfrozen_nodes:
        print("\n[에러] Freeze되지 않은 노드:")
        for node in unfrozen_nodes:
            print(f"- {node}")
    else:
        print("\n[성공] 모든 노드의 Transform이 Freeze되었습니다.")

    # 4. 자동 수정 기능 실행 (필요시)
    if unfrozen_nodes: # 예시로 unfrozen_nodes만 수정
        print(f"\n[수정] {len(unfrozen_nodes)}개의 노드에서 Freeze Transforms를 실행합니다.")
        validator.fix_history_and_transforms(unfrozen_nodes) # 이 함수가 히스토리와 트랜스폼을 동시에 수정
        print("수정 완료!")
    ```

## 🧠 Problem Solving & Optimization
-   **UI 워크플로우 개선:** 기존의 분리된 '씬 클린업' 버튼들(예: Unknown 노드 삭제, UV 세트 정리)을 메인 검사/수정 워크플로우에 통합하여 사용자 경험을 향상시키고 혼란을 줄였습니다. '검사 진행 내역' 패널을 추가하여 어떤 검사가 통과했는지도 명확하게 보여줍니다.
-   **UV 겹침 검사 정확성 향상:** `cmds.polyUVOverlap` 명령어의 특성(선택된 컴포넌트 대상)을 고려하여, 각 오브젝트의 모든 페이스를 선택한 후 검사를 실행하도록 로직을 수정했습니다. 이로 인해 UI에서 겹침이 있는 오브젝트를 클릭했을 때 올바른 오브젝트가 선택되며, 검사의 정확성과 신뢰도를 높였습니다. (성능 저하 가능성을 인지하고 이 방법을 채택했습니다.)
-   **코드 재사용성 및 유지보수성:** UI 로직(`scene_valiation_tool_ui.py`)과 핵심 검증 로직(`scene_validation_tool.py`)을 명확히 분리하여, 코드의 재사용성을 높이고 향후 기능 추가나 유지보수를 용이하게 했습니다.

---

### 설정 (Configuration)

이 툴의 일부 검사 항목은 외부 설정 파일을 통해 커스터마이징할 수 있습니다.

#### `naming_convention.config`

지오메트리의 네이밍 규칙을 설정합니다.
```ini
[naming_convention]
# 메쉬 그룹 이름이 이 접미사로 끝나야 합니다.
mesh_suffix = _geo
```
이 파일을 수정하여 프로젝트에 맞는 네이밍 규칙을 적용할 수 있습니다.
