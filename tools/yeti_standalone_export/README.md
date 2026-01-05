# Yeti Standalone Cache Exporter
> Maya GUI 없이 커맨드라인(`mayapy`) 환경에서 Yeti 캐시를 추출하여, 렌더팜(Render Farm) 자동화를 지원하는 파이프라인 툴입니다.

## 🎥 Demo
```bash
# 터미널에서 쉘 스크립트를 실행하여 Yeti 캐시를 추출하는 과정
$ ./run_yeti_standalone_export.sh --scenefile "/path/to/project/shot/scene.ma" --nodes "char:yeti_node"

# ==================================================================
# == Starting Yeti Standalone Cache Export
# ==================================================================
#
# Scene File: /path/to/project/shot/scene.ma
# Frame Range: 101-110
# Samples: 3
# Target Nodes: ['char:yeti_node']
#
# Caching node: char:yeti_node
# Writing cache file: /path/to/project/shot/cache/yeti/char_yeti_node.101.fur
# Progress: [████████████████████] 100%
#
# == Yeti Cache Export Finished
# ==================================================================
```
*(위 텍스트는 툴의 실제 실행 예시입니다.)*

## ✨ Features
- **Standalone 실행**: Maya GUI를 로드하지 않고 `mayapy`로 동작하여, 메모리 사용량과 실행 시간을 대폭 단축시킵니다.
- **자동 노드 감지**: 특정 노드를 지정하지 않으면 씬 파일 내의 모든 Yeti 노드를 자동으로 찾아 캐시를 추출합니다.
- **선택적 추출**: `--nodes` 인자를 사용하여 원하는 Yeti 노드만 지정하여 추출할 수 있습니다.
- **유연한 프레임 범위**: 캐시 프레임 범위를 직접 지정하거나, 지정하지 않을 경우 씬의 렌더 설정을 자동으로 사용합니다.
- **네임스페이스 지원**: 네임스페이스가 포함된 Yeti 노드 이름도 안정적으로 인식하고 처리합니다.

## 🛠 Tech Stack
- **Python**: 메인 프로그래밍 언어
- **Shell Script**: 실행 및 인자 전달을 위한 래퍼(Wrapper)
- **Maya Standalone**: `mayapy`를 사용한 백그라운드 실행 환경

## 🚀 Setup & Usage

### Command-line Arguments
스크립트 실행 시 사용할 수 있는 인자는 다음과 같습니다.

| 인자 (Argument) | 설명 | 필수 여부 |
| :--- | :--- | :--- |
| `--scene_file` | 캐시를 추출할 Maya 씬 파일의 전체 경로입니다. | **필수** |
| `--start_frame` | 캐시 추출 시작 프레임. (미지정 시 씬 설정 사용) | 선택 |
| `--end_frame` | 캐시 추출 종료 프레임. (미지정 시 씬 설정 사용) | 선택 |
| `--samples` | Yeti 캐시의 샘플 값. (기본값: 3) | 선택 |
| `--nodes` | 추출할 Yeti 노드의 이름을 하나 이상 지정합니다. (띄어쓰기로 구분) | 선택 |

### 실행 예시
터미널에서 `run_yeti_standalone_export.sh` 쉘 스크립트를 통해 아래와 같이 실행합니다.

```bash
# 기본 사용법: 씬 파일만 지정하여 모든 Yeti 노드를 씬 설정 범위로 추출
./run_yeti_standalone_export.sh --scene_file "/path/to/your/scene.ma"

# 고급 사용법: 특정 노드, 프레임 범위, 샘플 값을 모두 지정하여 추출
./run_yeti_standalone_export.sh \
    --scene_file "/path/to/your/scene.ma" \
    --start_frame 1001 \
    --end_frame 1050 \
    --samples 5 \
    --nodes "characterA:yeti_fur" "characterB:yeti_hair"
```

## 🧠 Problem Solving & Optimization
- **문제 정의**: 다수의 샷에 대한 Yeti 캐시를 렌더팜에 제출해야 할 때, 각 샷마다 Maya GUI를 직접 열어 캐시를 추출하는 작업은 매우 비효율적이고 많은 시간이 소요됩니다. 또한, GUI 환경은 리소스를 많이 차지하여 여러 작업을 동시에 처리하는 렌더팜 환경에 적합하지 않습니다.
- **해결 전략**: 이 문제를 해결하기 위해 **Maya의 GUI를 거치지 않는** 완전한 자동화 워크플로우를 설계했습니다. Maya의 독립 실행형 Python 인터프리터인 `mayapy`를 사용하여 백그라운드에서 씬을 열고 캐시 추출 커맨드만 실행하도록 했습니다. 모든 제어는 커맨드라인 인자(argument)를 통해 이루어지므로, 렌더팜 관리 소프트웨어(예: Deadline, Tractor)와 쉽게 연동할 수 있습니다.
- **구현**:
    1. **Argument Parsing**: Python의 `argparse` 모듈을 사용하여 커맨드라인에서 들어오는 다양한 인자들을 체계적으로 파싱하고 관리하도록 구현했습니다. 이를 통해 사용자는 `mayapy`와 스크립트의 내부 로직을 몰라도, 명확하게 정의된 인자만으로 원하는 작업을 수행할 수 있습니다.
    2. **안정적인 실행 환경**: 렌더팜 노드와 같은 비-GUI 환경에서도 안정적으로 실행되도록, 씬을 열고, Yeti 플러그인을 로드하고, 노드를 검색하고, 캐시를 추출한 후 씬을 닫는 전 과정을 스크립트 내에서 순차적으로 처리하도록 설계했습니다.

## 📜 Version History
- **v1.7** (2026-01-05)
  - 내부 파일 경로를 처리하는 `_get_root_path` 메소드 로직 개선
  - 커맨드라인 인자(argument) 처리 프로세스의 안정성 강화 및 리팩토링
- **v1.5** (2025-10-23)
  - 네임스페이스가 있는 Yeti 노드의 처리 방식을 개선
  - 원하는 Yeti 노드만 선택적으로 추출할 수 있도록 기능 추가
  - 커맨드라인 인자를 사용할 수 있도록 시스템 개선
- **v1.0** (2025-09-10)
  - `mayapy`를 이용한 Standalone 환경에서 기본 Yeti 캐시 추출 기능 구현
  - 씬 내의 모든 Yeti 노드를 대상으로 일괄 추출