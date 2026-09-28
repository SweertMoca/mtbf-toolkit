# AA PC: 처음 실행할 순서

**MD는 지침입니다. MD만으로는 실행 코드가 준비되지 않습니다.**
`COPY_THIS_bootstrap.py`를 복사·실행하면 코드, 설정, 템플릿과 문서 18개가 생성됩니다. MD를 하나씩 복사할 필요는 없습니다.

## 1. 파일 생성

GitHub에서 COPY_THIS_bootstrap.py를 열고 **Copy raw file** 버튼으로 전체 코드를 복사합니다.
버튼이 동작하지 않으면 Raw 화면의 전체 텍스트를 복사합니다. 줄 번호는 복사하지 않습니다.
AA PC의 VS Code에서 새 파일 `bootstrap_mtbf.py`에 붙여 넣고 UTF-8로 저장합니다.
그 파일이 있는 폴더의 터미널에서 실행합니다.

```text
python bootstrap_mtbf.py --dest mtbf_work_v2
```

Python 명령이 다르면 확인된 `python3` 또는 `py -3`를 사용합니다.
성공 메시지는 `Created and verified 18 files`입니다.
같은 폴더가 이미 있으면 다른 새 폴더명을 지정하세요. 기존 실험 결과를 덮어쓰지 않습니다.

## 2. 소프트웨어 시험

VS Code에서 생성된 `mtbf_work_v2` 폴더를 열고 터미널에서 실행합니다.

```text
python -m unittest discover -s tests -v
```

12개 시험이 통과해야 합니다. 실제 DFF 검증이 아니라 계산 소프트웨어 시험입니다.

## 3. Copilot에 복사할 요청

```text
AA_PC_FIRST_RUN.md, START_HERE.md, WORK_PC_AGENT.md를 읽고
단계 A(환경·넷리스트 조사)와 단계 B(정상 동작 확인)를 수행해줘.
이 PC는 AA PC라고 표기해.
대상은 내가 지정하는 DFF 넷리스트이고 PDK와 PrimeSim도 이 환경에 있어.
YOUR_DFF_CELL 및 YOUR_DFF_NETLIST.spice는 placeholder이므로 실제 파일에서 확인해.
필요하면 넷리스트 절대경로, PDK 모델 경로, 기존 PrimeSim 실행 예제를 나에게 물어봐.
핀·전압·reset 극성·well bias·모델 코너·실행 옵션을 추측하지 마.
코드를 새로 재작성하지 말고 제공된 scripts와 tests를 먼저 실행해.
터미널 실행이 불가능하면 실제 경로를 채운 정확한 명령을 알려줘.
결과를 results/aa_pc_001에 저장하고 WORK_PC_AGENT.md 양식의 RETURN_TO_REVIEWER.md를 작성해줘.
지금은 네 파라미터 추출이나 MTBF 추천까지 완료했다고 주장하지 마.
```

## 4. 사용자가 보충할 정보

- 실제 DFF 넷리스트 절대경로.
- PDK 모델 위치와 model section/corner 또는 기존 성공한 testbench.
- 확인 가능한 전원/온도/reset/well bias 조건. 모르면 미확인으로 남기기.
- 기존 PrimeSim 실행 예제가 있다면 명령과 엔진 종류.

모두 처음부터 직접 조사할 필요는 없습니다. Copilot이 프로젝트에서 찾지 못한 정보만 보충하세요.

## 5. 가져올 결과와 남은 일

첫 결과는 `results/aa_pc_001/RETURN_TO_REVIEWER.md`입니다.
오류가 있으면 관련 로그, 정상 동작에 성공하면 CK/D/Q 파형 요약을 함께 전달합니다.
자료 공유는 허용 범위에서만 합니다. PDK나 전체 넷리스트를 공개 GitHub에 올릴 필요는 없습니다.

단계 A/B 이후에도 tau_M, tau_S, TW1, TW2 추출과 독립 다단 검증이 남습니다.
AA PC에서 실제 시뮬레이션을 해야 하며 MD를 읽는 것만으로 완료되지는 않습니다.
