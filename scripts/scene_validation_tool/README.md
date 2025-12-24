# 씬 검수 툴 (Scene Validation Tool) - 모델링 팀용

## 1. 개요

이 툴은 **모델링 팀**이 리깅 팀이나 다음 파이프라인 단계로 데이터를 전달하기 전에, 데이터의 정합성을 스스로 검증하고 수정할 수 있도록 돕는 검수 자동화 스크립트입니다.

지오메트리의 네이밍 규칙, 변환 값, 히스토리, UV 상태 등 파이프라인에서 문제를 일으킬 수 있는 다양한 항목들을 자동으로 검사하고 일부는 자동으로 수정하는 기능을 제공합니다.

## 2. 주요 기능

이 툴은 다음과 같은 항목들을 검사하고 결과를 리스트업합니다.

### 지오메트리 및 트랜스폼
- **네이밍 규칙**: 그룹 이름이 `naming_convention.config` 파일에 지정된 접미사(`_geo` 등)로 끝나는지 검사합니다.
- **Freeze Transforms**: Translate, Rotate, Scale 값이 초기화되었는지 검사합니다.
- **History**: 지오메트리에 남아있는 히스토리를 검사합니다.
- **지오메트리 에러**:
    - **Ngons**: 5각형 이상의 면이 있는지 검사합니다.
    - **Non-manifold**: 비-다양체(Non-manifold) 구조의 지오메트리가 있는지 검사합니다.

### UV 관련
- **UV 에러**:
    - **No UV Sets**: UV 셋이 아예 없는 지오메트리를 검사합니다.
    - **Unassigned UVs**: UV가 할당되지 않은 면이 있는지 검사합니다.
- **다중 UV 셋 / 잘못된 이름**:
    - UV 셋이 2개 이상 존재하는 경우를 검사합니다.
    - UV 셋이 1개지만, 이름이 `map1`이 아닌 경우를 검사합니다.
- **UV 겹침 (Overlapping)**: 0-1 공간 내에서 UV가 서로 겹치는지 검사합니다.

### 씬 전반
- **레퍼런스 경로**: 절대 경로로 설정된 레퍼런스가 있는지 검사합니다.
- **Unknown 노드**: 씬에 남아있는 출처를 알 수 없는(Unknown) 노드를 검사하고 삭제할 수 있습니다.

## 3. 스크립트 구성

- **`scene_validation_tool.py`**: 검사를 수행하는 모든 핵심 로직이 `SceneValidatorCore` 클래스 안에 구현되어 있습니다. UI와 독립적으로 동작합니다.
- **`scene_valiation_tool_ui.py`**: `SceneValidatorCore` 클래스를 사용하여 사용자에게 검사 항목을 보여주고 상호작용하는 UI 스크립트입니다.

## 4. 사용법 (코어 클래스 직접 실행)

UI 없이 코어 클래스만으로도 검사를 실행할 수 있습니다.

```python
# Python 2/3 호환을 위해 importlib 또는 imp 사용
try:
    from importlib import reload
except ImportError:
    from imp import reload

# 코어 클래스 임포트 및 리로드
import scene_validation_tool
reload(scene_validation_tool)

from scene_validation_tool import SceneValidatorCore

# 1. 검증기 인스턴스 생성
validator = SceneValidatorCore()

# 2. 씬에 있는 모든 메쉬 가져오기
all_meshes = validator.get_all_mesh_transforms()
print(f"검사 대상 메쉬: {len(all_meshes)}개")

# 3. 특정 항목 검사 실행
unfrozen_nodes = validator.check_freeze_transforms(all_meshes)
if unfrozen_nodes:
    print("\n[에러] Freeze되지 않은 노드:")
    for node in unfrozen_nodes:
        print(f"- {node}")
else:
    print("\n[성공] 모든 노드의 Transform이 Freeze되었습니다.")

history_nodes = validator.check_history(all_meshes)
if history_nodes:
    print("\n[에러] 히스토리가 남은 노드:")
    for node in history_nodes:
        print(f"- {node}")
else:
    print("\n[성공] 모든 노드의 히스토리가 깨끗합니다.")

# 4. 자동 수정 기능 실행 (필요시)
if history_nodes or unfrozen_nodes:
    nodes_to_fix = list(set(history_nodes + unfrozen_nodes))
    print(f"\n[수정] {len(nodes_to_fix)}개의 노드에서 히스토리 삭제 및 Freeze를 실행합니다.")
    validator.fix_history_and_transforms(nodes_to_fix)
    print("수정 완료!")
```

## 5. 설정 (Configuration)

이 툴의 일부 검사 항목은 외부 설정 파일을 통해 커스터마이징할 수 있습니다.

### `naming_convention.config`

지오메트리의 네이밍 규칙을 설정합니다.

```ini
[naming_convention]
# 메쉬 그룹 이름이 이 접미사로 끝나야 합니다.
mesh_suffix = _geo
```

이 파일을 수정하여 프로젝트에 맞는 네이밍 규칙을 적용할 수 있습니다.
