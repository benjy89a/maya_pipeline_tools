# 🛠️ Maya Sim Origin Stabilizer

마야(Maya) 내 시뮬레이션 작업 시, 월드 좌표 오차로 인한 지터링(Jittering) 현상을 방지하기 위해 **객체를 원점(Origin)으로 역계산하여 고정**시켜주는 파이프라인 자동화 툴입니다.


## 📌 Overview
대규모 씬에서 캐릭터가 원점(0,0,0)에서 멀리 떨어져 있을 경우, 부동 소수점 연산 오류로 인해 nCloth나 가이드 커브 시뮬레이션이 불안정해지는 문제가 발생합니다. 이 스크립트는 **OpenMaya API 2.0**을 사용하여 복잡한 행렬 계산을 자동화하고 아티스트에게 안정적인 작업 환경을 제공합니다.

## ✨ Key Features
* **Matrix-based Alignment:** 기준 로케이터의 `Inclusive Matrix`를 역산(`Inverse`)하여 타겟을 정밀하게 원점에 배치합니다.
* **Space Switch System:** `Set Driven Keyframe`을 통해 클릭 한 번으로 'World'와 'Origin' 공간을 자유롭게 전환할 수 있습니다.
* **Non-Destructive Workflow:** 리깅 그룹 내에 원래의 월드 행렬 값을 보존(`originalWorldMatrix` 속성)하여 데이터 유실을 방지합니다.
* **Validation Check:** 타겟의 트랜스폼 값이 Frozen 상태인지 자동 체크하여 오프셋 발생 가능성을 사전에 경고합니다.

## 🛠 Tech Stack
* **Language:** Python 3
* **Libraries:** `maya.cmds`, `maya.api.OpenMaya` (API 2.0)
* **Concepts:** Inverse Matrix, World Space Transformation, SDK(Set Driven Keyframe)


## 🚀 Usage

### 1. Installation
`scripts` 폴더에 해당 파이썬 파일을 위치시킨 후 마야 내 스크립트 에디터에서 아래와 같이 호출합니다.

### 2. Run Script
```python
import sim_origin_stabilizer # 파일명에 맞춰 변경하세요

# loc_name: 기준이 될 로케이터 이름
# sim_target: 시뮬레이션 대상 오브젝트 (선택 사항)
sim_origin_stabilizer.create_sim_origin_stabilizer(loc_name='locator1', sim_target='char_mesh')