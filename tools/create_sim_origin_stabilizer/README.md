# Sim Origin Stabilizer
> 대규모 씬에서 발생하는 좌표 오차(Jittering)를 해결하기 위해, 시뮬레이션 소스 오브젝트를 가상의 원점으로 고정시켜주는 Maya 파이프라인 툴입니다.

## ✨ Features
- **정확한 원점 정렬**: `maya.api.OpenMaya`를 사용하여 기준 로케이터의 월드 매트릭스를 역연산(`Inverse Matrix`)하고, 타겟 오브젝트를 월드 원점(0,0,0)에 정밀하게 배치합니다.
- **원클릭 공간 변환 (Space Switch)**: `Set Driven Key`를 이용하여 `World` 공간(원본 위치)과 `Origin` 공간(시뮬레이션용 원점 위치)을 속성(Attribute) 슬라이더로 손쉽게 전환할 수 있는 시스템을 자동으로 구축합니다.
- **비파괴적 워크플로우**: 원본 월드 매트릭스 정보를 별도의 노드(`originalWorldMatrix` 속성)에 안전하게 보관하여, 언제든지 원본 상태로 복원할 수 있습니다.
- **사전 유효성 검사**: 타겟 오브젝트의 `Transform` 값이 Freeze 상태인지 자동으로 확인하여, 이중 변환으로 인한 예기치 않은 오프셋 발생을 사전에 방지하고 사용자에게 경고합니다.

## 🛠 Tech Stack
- **Python**: 메인 프로그래밍 언어
- **Maya API**: `maya.cmds` 및 `maya.api.OpenMaya` (정밀한 행렬 계산용)
- **Rigging Concepts**: Inverse Matrix, World Space Transformation, Set Driven Key (SDK)

## 🚀 Setup & Usage
1.  **설치**: `create_sim_origin_stabilizer.py` 파일을 Maya 스크립트 경로에 등록된 폴더 (예: `maya/scripts`)에 배치합니다.
2.  **실행**: Maya의 스크립트 에디터(Python 탭)에서 아래 코드를 실행합니다.

```python
from importlib import reload
import create_sim_origin_stabilizer

# 개발 중에는 reload를 사용하여 최신 코드를 반영하는 것이 좋습니다.
reload(create_sim_origin_stabilizer)

# loc_name: 월드 공간의 기준점이 될 로케이터의 이름
# sim_target: 원점으로 옮길 시뮬레이션 대상의 최상위 그룹 이름
create_sim_origin_stabilizer.create_sim_origin_stabilizer(
    loc_name='DRV_locator', 
    sim_target='GRP_char'
)
```

## 🧠 Problem Solving & Optimization
- **문제 정의**: 대규모 씬에서 캐릭터가 월드 원점(0,0,0)에서 수 킬로미터 떨어져 있을 경우, 컴퓨터의 부동 소수점 정밀도 한계로 인해 좌표 연산에 미세한 오차가 누적됩니다. 이 오차는 nCloth, 헤어 시뮬레이션 등에서 심각한 **떨림(Jittering) 현상**을 유발하여 결과물의 품질을 저하시킵니다.

- **해결 전략**: 전체 씬을 원점으로 옮기는 것은 비효율적이므로, 시뮬레이션에 필요한 오브젝트만 **"가상의 원점"**으로 가져오는 방법을 선택했습니다. 기준 로케이터를 캐릭터의 발밑에 두고, 이 로케이터의 월드 공간 변환 값을 역으로 적용하여 캐릭터 그룹 전체를 월드 원점으로 되돌리는 로직을 구현했습니다. 특히, 프리 시뮬레이션 단계에서 시뮬레이션 에셋이 월드 애니메이션 위치로 이동하는 동안 에셋이 손상될 가능성이 매우 높으므로, 이 스크립트를 사용하여 에셋 손상을 방지하고 데이터 무결성을 유지하는 것이 주요 목적입니다.
- **기술적 구현**:
    1.  **정밀한 행렬 연산**: 미세한 오차도 허용되지 않는 좌표 변환을 위해, 일반 `maya.cmds` 대신 `maya.api.OpenMaya`의 `MMatrix`를 사용했습니다. 이는 더 높은 정밀도를 보장하고 복잡한 행렬 연산(역행렬 계산 등)을 효율적으로 처리합니다.
    2.  **자동화된 공간 전환 시스템**: 아티스트가 수동으로 좌표를 맞추는 대신, `Set Driven Key`를 사용하여 `space`라는 커스텀 속성을 만들었습니다. 이 속성 값을 0 또는 1로 조절하는 것만으로 'World'와 'Origin' 공간을 오갈 수 있어, 직관적이고 반복 작업에 용이한 워크플로우를 제공합니다.
    3.  **데이터의 안정성**: 변환 과정에서 원본 위치 데이터가 소실될 위험을 방지하기 위해, 계산된 역행렬 값을 별도의 `transform` 노드 내 `originalWorldMatrix` 속성에 저장했습니다. 이는 언제든지 원본 상태로 100% 복원할 수 있음을 보장하는 비파괴적 설계의 핵심입니다.
