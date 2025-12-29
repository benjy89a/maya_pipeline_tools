# 쉐이더맵 익스포터/임포터 (Shader Map Exporter/Importer)
> Maya 씬의 쉐이더 할당 정보를 JSON 파일로 추출하고, 다른 씬에서 레퍼런스 에셋을 기준으로 쉐이더를 다시 적용합니다.

## 🎥 Demo
![Demo GIF](./demo.gif) 
*데모 GIF는 준비 중입니다.*

## ✨ Features
- **정확한 데이터 추출**: 오브젝트 전체는 물론, 페이스(Face) 단위로 할당된 쉐이더 정보까지 정확하게 추출합니다.
- **네임스페이스 자동 처리**: 레퍼런스(Reference) 에셋의 네임스페이스를 자동으로 감지하여 복잡한 씬에서도 안정적으로 쉐이더를 적용합니다.
- **파일 기반 워크플로우**: 에셋 이름과 1:1로 매칭되는 JSON 파일을 생성하여 데이터를 명확하고 직관적으로 관리할 수 있습니다.

## 🛠 Tech Stack
- Python 3
- Maya.cmds

## 🚀 Setup & Usage

### 1. 쉐이더 정보 추출 (Export)
1. Maya에서 쉐이더 정보를 추출할 지오메트리들을 선택합니다.
2. 아래 Python 코드를 실행하여 씬 파일과 동일한 경로에 `.json` 파일을 생성합니다.

```python
import importlib
import export_shader_map_to_json

# 모듈 리로드
importlib.reload(export_shader_map_to_json)

# 선택한 지오메트리의 쉐이더 정보를 "my_asset_shader_map.json" 파일로 저장
export_shader_map_to_json.export_shader_map_to_json("my_asset_shader_map.json")
```

### 2. 쉐이더 정보 적용 (Import)
1. 쉐이더를 적용할 Maya 씬(레퍼런스 에셋 포함)을 엽니다.
2. 아래 Python 코드를 실행하면, 스크립트가 씬의 레퍼런스 에셋과 이름이 일치하는 JSON 파일을 찾아 쉐이더를 자동으로 적용합니다.

```python
import importlib
import import_shader_map_from_json

# 모듈 리로드
importlib.reload(import_shader_map_from_json)

# JSON 파일들이 저장된 폴더 경로 지정
json_folder_path = r"C:\path\to\your\json_files" 
import_shader_map_from_json.import_shaders_from_json(json_folder_path)
```

## 📂 JSON 파일 구조 예시
JSON 파일은 추출 시 선택한 각 지오메트리(오브젝트)의 이름을 최상위 키로 사용합니다. 각 키의 값은 해당 오브젝트에 할당된 쉐이더 정보 목록입니다.

각 쉐이더 정보는 다음을 포함합니다:
- `sg_name`: 쉐이딩 그룹(Shading Group)의 이름입니다.
- `members`: 해당 쉐이더가 적용된 컴포넌트 목록입니다. 오브젝트 전체에 적용된 경우 쉐이프 노드 이름이, 페이스(Face)에만 적용된 경우 `.f[]` 형식의 컴포넌트 이름이 저장됩니다.

아래는 `pCube1`에는 단일 쉐이더를 오브젝트 전체에 할당하고, `pCylinder1`에는 기본 쉐이더와 함께 두 개의 다른 쉐이더를 특정 페이스 영역에 각각 할당했을 때 생성되는 JSON 파일의 예시입니다. 이처럼 하나의 파일 안에 여러 오브젝트의 정보와 다양한 할당 방식(오브젝트, 페이스)이 모두 함께 저장될 수 있습니다.

```json
{
    "pCube1": [
        {
            "sg_name": "lambert2SG",
            "members": [
                "pCubeShape1"
            ]
        }
    ],
    "pCylinder1": [
        {
            "sg_name": "plasticSG",
            "members": [
                "pCylinderShape1"
            ]
        },
        {
            "sg_name": "metalSG",
            "members": [
                "pCylinderShape1.f[100:119]"
            ]
        },
        {
            "sg_name": "labelSG",
            "members": [
                "pCylinderShape1.f[80:99]"
            ]
        }
    ]
}
```

## 🧠 Problem Solving & Optimization
- **파이프라인 안정성 확보**: 애니메이션, 렌더링 등 다른 부서로 데이터를 전달하는 과정에서 쉐이더가 유실되는 문제를 해결하기 위해 개발되었습니다. 씬에 복잡하게 구성된 레퍼런스 에셋의 네임스페이스를 자동으로 처리하여, 수작업 없이 안정적으로 쉐이더를 재할당할 수 있도록 설계했습니다.