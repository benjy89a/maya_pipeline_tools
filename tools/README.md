# Maya 파이프라인 툴 포트폴리오

이 저장소는 Autodesk Maya 내의 다양한 워크플로우를 자동화하고 간소화하기 위해 설계된 Python 기반 파이프라인 툴 모음입니다. 각 툴은 아티스트와 테크니컬 디렉터를 위해 효율성, 안정성, 그리고 사용 편의성에 중점을 두고 개발되었습니다.

아래는 이 포트폴리오에 포함된 툴들의 개요입니다. 각 툴의 제목을 클릭하면 데모, 주요 기능, 기술적 문제 해결 접근 방식 등 상세한 문서를 확인할 수 있습니다.

---

## 🛠️ 툴 개요 (Tools Overview)

1.  ### [Casper | Maya 스크립트 런처](./casper/README.md)
    > 지정된 폴더 구조를 탐색하여 Python 스크립트를 탭 기반 UI로 자동 구성하고 실행하는 Maya용 스크립트 런처입니다.

2.  ### [Sim Origin Stabilizer | 시뮬레이션 원점 안정화 툴](./create_sim_origin_stabilizer/README.md)
    > 대규모 씬에서 발생하는 좌표 오차(Jittering)를 해결하기 위해, 시뮬레이션 오브젝트를 가상의 원점으로 고정시켜 안정적인 계산을 지원하는 리깅을 생성하는 파이프라인 툴입니다.

3.  ### [Shader Map Exporter/Importer | 쉐이더맵 추출 및 적용 툴](./export_shader_map_to_json/README.md)
    > Maya 씬의 쉐이더 할당 정보(페이스 단위 할당 포함)를 JSON 파일로 추출하고, 다른 씬의 레퍼런스 에셋에 다시 적용하여 파이프라인 전반의 일관성을 보장하는 툴입니다.

4.  ### [Scene Validation Tool | 씬 검증 툴](./scene_validation_tool/README.md)
    > Maya 씬의 모델링 데이터를 검증하고 수정하는 자동화 툴입니다. 잘못된 네이밍 컨벤션, 고정되지 않은 트랜스폼, 지오메트리 에러(N각형, 논매니폴드), 다양한 UV 문제 등을 검사하고 자동 수정 옵션을 제공합니다.

5.  ### [Yeti Standalone Cache Exporter | Yeti 스탠드얼론 캐시 추출 툴](./yeti_standalone_export/README.md)
    > `mayapy`(Maya 독립 실행형 Python 인터프리터)를 사용하여 Yeti 헤어 및 퍼(fur) 캐시를 추출하는 커맨드라인 툴입니다. Maya GUI를 로드하지 않고 배치 처리가 가능하여 렌더팜 자동화를 위해 설계되었습니다.

---

## 📂 폴더 구조 (Folder Structure)

이 프로젝트는 핵심 로직, Maya 전용 유틸리티, 그리고 개별 툴을 분리하기 위해 모듈식 구조를 따릅니다.

```
maya_pipeline_tools/
├── core/                   # 여러 툴에서 공용으로 사용하는 순수 파이썬 모듈
├── maya_utils/             # Maya 전용 공통 유틸리티 (cmds, OpenMaya 등)
└── tools/                  # 실제 파이프라인 툴들이 위치하는 메인 디렉토리
    ├── casper/
    ├── create_sim_origin_stabilizer/
    ├── export_shader_map_to_json/
    ├── scene_validation_tool/
    └── yeti_standalone_export/
```

이 구조는 확장성과 유지보수성을 고려하여 설계되었으며, 새로운 툴을 쉽게 추가할 수 있습니다.
