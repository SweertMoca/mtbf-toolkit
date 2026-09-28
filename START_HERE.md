# MTBF 재현 패키지 — 사용자가 먼저 읽을 파일

이 폴더 전체를 업무용 컴퓨터로 복사하세요. Python 3.9 이상과 표준 라이브러리만 사용합니다. 별도의 pip 설치는 필요 없습니다. PDK와 원본 넷리스트는 이동하거나 수정할 필요가 없습니다.

현재 상태: 계산·검사·분석 도구 구현 완료. 실제 PDK와 PrimeSim을 이용한 실험은 아직 수행하지 않았습니다. 예제 숫자는 가상 값이며 설계에 사용하면 안 됩니다.

## 1. VS Code에서 할 일

1. 이 폴더를 VS Code의 작업 폴더로 엽니다. 기존 업무 프로젝트에서 작업한다면 이 폴더를 하위 폴더로 복사해도 됩니다.
2. Copilot 채팅에 아래 문장을 복사합니다. 파일을 읽지 못하면 WORK_PC_AGENT.md 내용을 채팅에 붙여 넣으세요.

```text
이 작업 폴더의 WORK_PC_AGENT.md와 START_HERE.md를 읽고 지침대로 실행해줘.
먼저 단계 A(환경 및 넷리스트 조사)와 단계 B(정상 동작 확인)를 수행해줘.
넷리스트 이름은 DFFRPQLV_D1_N_M7P5TL_C60L08_nominal_max_25c.spice야.
실제 파일 경로와 PDK는 이 컴퓨터에 있어. 지정된 작업 폴더에서 찾고, 못 찾으면 필요한 경로만 물어봐.
경로, 핀 기능, 모델 코너, 전압, 실행 옵션을 추측하지 마.
가능한 검사는 직접 실행하고, 파일만 만들고 완료했다고 하지 마.
터미널 실행이 불가능하면 내가 실행할 정확한 명령을 실제 경로로 완성해서 줘.
결과는 새 results/work_pc_001 폴더에 저장하고 RETURN_TO_REVIEWER.md를 작성해줘.
아직 검증되지 않은 MTBF 숫자로 DFF 개수를 추천하지 마.
```

3. Copilot이 넷리스트/PDK 위치를 찾지 못할 때만 실제 경로를 알려주세요. 실행 권한 요청이 나오면 명령이 해당 프로젝트의 검사 또는 시뮬레이션인지 확인하고 진행합니다.
4. 끝나면 results/work_pc_001/RETURN_TO_REVIEWER.md와 필요한 로그를 이쪽에 전달하세요. 전체 넷리스트가 포함된 inventory는 업무용 PC에 남겨도 됩니다. 회사 반출 기준을 따르세요.

Copilot 모델 이름을 알아야 시작할 수 있는 작업은 아닙니다. 이 패키지는 명령 실행과 결과 형식을 고정해 모델의 추측을 줄입니다. 다만 MD만으로 준수를 보장할 수는 없습니다.

## 2. 직접 실행하는 최소 명령

터미널의 현재 폴더를 이 패키지로 맞춥니다. 아래 `python`이 없으면 업무용 PC에서 확인된 `python3`, `py -3` 또는 Python 실행 파일 경로로 바꾸세요.

```text
python -m unittest discover -s tests -v
python scripts/inspect_netlist.py "실제_넷리스트_절대경로" --out results/inventory_001
python scripts/mtbf.py --parameters config/parameters.synthetic.json --application config/application.example.json --out results/demo_002
```

출력 폴더가 이미 존재하면 덮어쓰지 않고 중단합니다. 다음 실행은 `_002`, `_003`처럼 새 폴더를 지정하세요. 코드 시험용 임시 디렉터리를 제외하고 원본 파일을 삭제하는 동작은 없습니다.

## 3. 이 폴더의 도구

| 파일 | 현재 기능 |
|---|---|
| scripts/inspect_netlist.py | M/X/R/C 목록, SUBCKT 핀, 모델 및 include 선언, 원본 해시 추출 |
| scripts/check_environment.py | OS/Python/넷리스트 경로/지정 실행 파일 확인; 라이선스와 모델은 별도 확인 |
| scripts/mtbf.py | 논문 식 (9), (17), (19), 실제 개수 K별 MTBF 계산, CSV/JSON/Markdown 보고서 |
| scripts/run_case.py | 템플릿 치환, 명시적 argv로 시뮬레이터 실행, 로그/실행 기록, 타임아웃 |
| scripts/analyze.py | 파형 차이의 지수 피팅과 식 (18)에 따른 aperture 환산 |
| scripts/boundary.py | 측정 콜백을 받아 임계값 경계를 이분 탐색하는 함수 |
| tests/test_tools.py | 수식, 실패 처리, 로그 계산, 파라미터 복원, 넷리스트 파싱 시험 |

`run_case.py`는 PrimeSim 전용 완성 드라이버가 아닙니다. 설치된 엔진의 명령·출력 형식에 맞춘 어댑터가 필요합니다. `boundary.py` 역시 실제 시뮬레이션을 호출하는 evaluate 함수가 연결되어야 합니다. 이 연결 작업은 WORK_PC_AGENT.md에 규정했습니다.

우선 단계 A/B 결과를 확보하세요. 네 파라미터가 없는데 MTBF 계산부터 실험값처럼 사용하는 것은 순서가 잘못된 것입니다.
