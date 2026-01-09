# Maya Pipeline Tools

> Autodesk Maya 파이프라인 자동화 및 효율성 향상을 위한 파이썬 스크립트 모음입니다.

## ✨ 주요 기능 (Features)

이 프로젝트는 Maya 파이프라인의 다양한 단계를 지원하는 여러 도구를 포함합니다.

- **Casper:** 다양한 에셋 및 샷 작업을 실행하기 위한 UI 기반의 툴 로더입니다.
- **Create Sim Origin Stabilizer:** 시뮬레이션 원점을 안정화시켜주는 보조 도구입니다.
- **Shader Map Exporter/Importer:** 복잡한 셰이더 네트워크 정보를 JSON 파일로 내보내고 가져옵니다.
- **Scene Validation Tool:** 씬 파일이 명명 규칙과 같은 프로젝트 규칙을 준수하는지 검사합니다.
- **Yeti Standalone Exporter:** Yeti 헤어 시스템 데이터를 커맨드라인으로 익스포트하는 툴입니다.

## 🛠 사용 기술 (Tech Stack)

- **언어:** Python 3
- **주요 API:** `maya.cmds`, `maya.api.OpenMaya`
- **핵심 원칙:**
    - UI 제작에는 `PySide2` 사용
    - Maya 씬 조작은 `maya.cmds`를 우선적으로 활용
    - 수학적 계산 및 성능 최적화가 필요한 부분에서는 `maya.api.OpenMaya` (om2)를 제한적으로 사용

## 🧠 아키텍처 및 문제 해결 (Architecture & Problem Solving)

이 프로젝트는 Maya 파이프라인 툴 개발에 대한 깊은 이해를 보여주기 위해 신중하게 설계되었습니다.

- **모듈화된 구조:**
    - `core/`: Maya에 종속되지 않는 순수 Python 유틸리티 모듈 (e.g., 로깅, 파일 입출력)을 분리하여 재사용성을 극대화했습니다.
    - `maya_utils/`: `maya.cmds` 또는 `om2`를 사용하는 Maya 전용 유틸리티 함수를 모아두어, 여러 툴에서 공통적으로 필요한 기능을 효율적으로 관리합니다.

- **Maya API 활용 전략:**
    - **`maya.cmds` 중심 접근:** 대부분의 씬 조작(객체 생성, 수정, 쿼리)은 간결하고 직관적인 `maya.cmds`를 사용하여 가독성과 유지보수성을 높였습니다.
    - **`OpenMaya`를 통한 성능 최적화:** `maya.cmds`의 성능 한계가 명확한 특정 상황(e.g., 대규모 벡터/행렬 연산, 복잡한 지오메트리 데이터 처리)에서는 `maya.api.OpenMaya` (om2)를 활용하여 계산 효율을 최적화했습니다. 이는 API의 장단점을 이해하고 상황에 맞게 최적의 도구를 선택하는 능력을 입증합니다.

- **확장 가능한 툴셋:**
    - 각 도구는 `tools/` 디렉터리 아래에 독립적인 패키지 형태로 구성되어 있어 새로운 기능을 추가하거나 기존 기능을 수정하기 용이합니다. 이러한 구조는 프로젝트가 커지더라도 체계적으로 관리할 수 있게 해줍니다.

---

## 📂 폴더 구조 (Folder Structure)

이 프로젝트는 핵심 로직, Maya 전용 유틸리티, 그리고 개별 툴을 분리하기 위해 모듈식 구조를 따릅니다.

```
maya_pipeline_tools/
├── core/                   # 여러 툴에서 공통으로 사용하는 순수 파이썬 모듈
├── maya_utils/             # Maya 전용 공통 유틸리티 (cmds, OpenMaya 등)
└── tools/                  # 실제 파이프라인 툴이 위치하는 메인 디렉터리
    ├── casper/
    ├── create_sim_origin_stabilizer/
    ├── export_shader_map_to_json/
    ├── scene_validation_tool/
    └── yeti_standalone_export/
```

이 구조는 확장성과 유지보수성을 고려하여 설계되었으며, 새로운 툴을 쉽게 추가할 수 있습니다.
