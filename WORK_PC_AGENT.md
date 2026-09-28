# AA PC의 Copilot 실행 지침

## 목적과 절대 규칙

Beer et al., MTBF Bounds for Multistage Synchronizers (ASYNC 2013)의 모델을 실제 셀에 적용한다. 실제 DFF 개수 K와 논문 N=K-1을 구분한다. 계산 대상은 모델 MTBF 하한이며 실측 수명이 아니다.

1. 원본 PDK, 원본 셀 넷리스트, 기존 프로젝트 결과를 변경하지 않는다. 새 작업 디렉터리에만 생성한다.
2. 확인된 명령은 직접 실행한다. 파일 작성, 종료 코드 0, 좋은 R2만으로 시뮬레이션 또는 추출 성공을 선언하지 않는다.
3. 자료를 찾지 못하면 missing으로 기록한다. 값·모델·핀 극성·시뮬레이터 옵션을 만들어 넣지 않는다.
4. M/X 이름만으로 master/slave를 지정하지 않는다. 논리 연결과 파형 증거를 제시한다.
5. 상태는 missing, failed, candidate, validated 중 하나로 기록한다. validated는 전체 검증 증거와 검토자 승인 기록이 있을 때만 사용한다.
6. 계산기/테스트의 안전 검사를 통과시키려고 삭제하거나 완화하지 않는다. 코드 수정이 필요하면 이유와 diff를 기록한다.
7. 실제 PDK 데이터를 인터넷/외부 서비스에 업로드하지 않는다. 공유용 결과와 내부 회로 상세 보고서를 구분한다.
8. 단계가 막혀도 수행 가능한 독립 검사는 완료한다. 미완료 이유를 기록한다.

## 단계 A — 환경·회로 조사

- 작업 폴더 및 사용자가 지정한 PDK/넷리스트 위치에서 조사한다. 전체 디스크를 무작정 검색하지 않는다.
- OS, Python 버전, PrimeSim의 실제 엔진 이름과 버전, 실행 파일, 라이선스 접근 여부를 확인한다. 기존 성공 사례가 있으면 그 실행법을 우선 사용한다. 버전 확인 옵션도 로컬 도움말/기존 기록을 따른다.
- `python -m unittest discover -s tests -v` 실행 및 로그 저장.
- `python scripts/check_environment.py --netlist "실제경로" --simulator "확인된실행파일" --out results/work_pc_001/environment.json` 실행. 실행 파일이 아직 없으면 --simulator를 생략하고 미확인으로 남긴다. 출력 부모 폴더를 먼저 만든다.
- `inspect_netlist.py`를 실제 파일에 실행. M 소자가 있는지, X가 호출하는 정의가 어디 있는지 확인. `.include`/`.lib`를 읽어 필요한 모델과 section이 실제 해석되는지 추적한다. 검사기는 include를 자동 해석하지 않는다.
- 외부 핀 CK D Q R VDD VNW VPW VSS는 사진에서 전사한 정보다. 실제 .SUBCKT와 비교한다. R의 기능·극성, well bias, 전원 전압은 라이브러리 자료 또는 회로 분석으로 확인한다.
- 이름에 있는 nominal/max/25c를 곧바로 transistor corner, RC corner, 시뮬레이션 온도로 간주하지 않는다. 각각의 근거를 기록한다.
- full inventory는 내부 자료다. 공유용 요약에는 파일 해시, 소자 수, 모델 참조 해결 여부, 핀 확인 결과, 미해결 사항을 기록한다.

산출물: environment.json, inventory 디렉터리, topology_notes.md, tests.log, RETURN_TO_REVIEWER.md.

## 단계 B — 정상 동작과 로컬 어댑터

- templates/nominal_check.sp.in을 복사하고 실제 엔진 문법에 맞춘다. 모델 setup 파일에서 검증된 .lib 또는 .include 구문을 작성한다.
- 초기화/reset 시퀀스, 전원, well bias를 명시한다. reset 비활성 상수만으로 초기 상태가 보장된다고 가정하지 않는다.
- D가 클록 경계에서 충분히 떨어져 바뀌는 0→1 및 1→0 시험을 만들고 여러 클록 주기에서 D→Q 기능과 reset 동작을 확인한다.
- PULSE의 plateau 폭과 50% crossing 사이 high time은 다르다. duty와 시간 원점은 CK 50% crossing 기준으로 측정하여 기록한다.
- 기존 정상 실행 명령과 출력 export 형식을 확인해 run 설정의 command_argv를 실제 값으로 채운다. 각 인수는 배열 원소 하나다. shell 연산자 `>`, `&&`는 넣지 않는다.
- `run_case.py`의 기본은 render-only다. 실제 실행 전에 설정과 생성된 deck을 확인한다. 필요한 항목을 모두 채우고 reviewed_for_local_environment=true로 바꾼 후 --execute를 사용한다.
- stdout/stderr뿐 아니라 엔진이 작성한 listing, 측정 파일의 에러/미수렴/미정의 모델/측정 실패를 검사한다.
- 시간, D, CK, Q 및 관측할 내부 노드를 SI 단위 CSV로 export하는 로컬 어댑터를 작성한다. 엔진의 파형 내보내기 기능 또는 확인된 공식 형식을 이용한다. 알려지지 않은 바이너리를 임의로 해석하지 않는다.
- 원본 넷리스트와 실제 모델 setup의 해시, 버전, 실행 명령, 정확도 옵션을 기록한다.

여기까지가 첫 전달의 필수 범위다. RETURN_TO_REVIEWER.md에 성공 여부와 다음 실행에 필요한 조건을 기록한다. 단계 C/D는 CHARACTERIZATION_PROTOCOL.md의 조건이 충족되고 작업 지시가 있을 때 진행한다.

## 단계 C/D — 특성 추출·검증을 진행할 때

CHARACTERIZATION_PROTOCOL.md를 따른다. 추출 코드를 새 scripts/local_adapter.py에 작성하고 인터페이스를 문서화한다. evaluate(offset_s)는 한 회의 성공한 시뮬레이션에서 지정 관측 시점의 전압을 반환해야 한다. 실패를 0 V로 반환하지 말고 예외를 발생시킨다. waveform CSV, 측정값, 실행 디렉터리를 연결해 추적할 수 있게 한다.

독립 조건의 체인 검증 전에 parameters 파일을 validated로 바꾸지 않는다. 모델이 맞지 않으면 불일치를 보고하며 임의 보정 상수로 숨기지 않는다.

## RETURN_TO_REVIEWER.md 필수 형식

```text
실행 일시 / 작업 폴더:
현재 완료 단계:
Python / PrimeSim 엔진 / 버전:
실제 실행 명령:
넷리스트 SHA256 / 소자 수:
모델 참조 해결 여부:
핀 순서 확인 / reset / well bias 확인 근거:
사용 PVT / 입력 및 클록 slew / 부하:
정상 기능 시험 결과와 관련 로그 경로:
master/slave 후보와 연결·파형 근거 (미확정 가능):
실패 또는 경고 원문:
수정한 파일과 이유:
다음에 필요한 정보:
반출 가능한 첨부 결과 목록:
```
