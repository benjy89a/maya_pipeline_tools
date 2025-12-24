# 쉐이더 할당 정보 추출 및 복구 툴

이 툴은 Maya 씬의 지오메트리에 적용된 쉐이더 할당 정보를 JSON 파일로 추출(Export)하고, 필요할 때 이 정보를 사용해 쉐이더를 다시 복구(Restore)하는 기능을 제공합니다.

애니메이션, 렌더링 등 다른 부서로 데이터를 넘기기 전 쉐이더 정보를 백업하거나, 레퍼런스로 구성된 씬에서 쉐이더 할당이 유실되었을 때 일괄적으로 복구하는 파이프라인에 유용하게 사용할 수 있습니다.

---

## 주요 기능

- **정확한 정보 추출**: 오브젝트 전체에 할당된 쉐이더뿐만 아니라, 페이스(Face) 단위로 할당된 쉐이더 정보까지 정확하게 추출합니다.
- **네임스페이스 지원**: 레퍼런스(Reference) 에셋의 네임스페이스를 자동으로 감지하고 처리하여, 복잡한 씬에서도 안정적으로 동작합니다.
- **파일 기반 워크플로우**: 에셋 이름과 1:1로 매칭되는 JSON 파일을 생성하여 데이터를 명확하고 직관적으로 관리할 수 있습니다.

---

## 파일 구성

- **`export_shader_mapt_to_json.py`**: 선택된 오브젝트의 쉐이더 정보를 추출하여 JSON 파일로 저장하는 스크립트입니다.
- **`restore_shader_map_from_json.py`**: 지정된 폴더의 JSON 파일들을 읽어, 현재 씬의 레퍼런스 에셋에 쉐이더를 다시 적용하는 스크립트입니다.

---

## 사용 방법

### 1. 쉐이더 정보 추출 (Export)

1. Maya에서 쉐이더 정보를 추출할 지오메트리들을 선택합니다.
2. 아래와 같이 Python 스크립트 편집기에서 실행합니다. JSON 파일은 현재 씬 파일과 같은 경로에 저장됩니다.

```python
# 스크립트를 Maya에 로드하고 실행
# Python 2/3 호환을 위해 imp 또는 importlib 사용
try:
    from importlib import reload
except ImportError:
    from imp import reload

import export_shader_mapt_to_json
reload(export_shader_mapt_to_json)

# "my_asset_shader_map.json" 라는 이름으로 파일 저장
export_shader_mapt_to_json.export_shader_map_to_json("my_asset_shader_map.json")
```

### 2. 쉐이더 정보 복구 (Restore)

1. JSON 파일들이 저장되어 있는 폴더 경로를 확인합니다.
2. 쉐이더를 복구할 Maya 씬(레퍼런스 에셋 포함)을 엽니다.
3. 아래와 같이 Python 스크립트 편집기에서 실행합니다. 스크립트가 씬의 레퍼런스를 확인하고, 이름이 일치하는 JSON을 찾아 쉐이더를 자동으로 복구합니다.

```python
# 스크립트를 Maya에 로드하고 실행
try:
    from importlib import reload
except ImportError:
    from imp import reload

import restore_shader_map_from_json
reload(restore_shader_map_from_json)

# JSON 파일들이 들어있는 폴더 경로를 지정
json_folder_path = r"C:\path\to\your\json_files"
restore_shader_map_from_json.restore_shaders_from_json(json_folder_path)
```
