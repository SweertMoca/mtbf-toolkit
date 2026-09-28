# PrimeSim 특성화 절차

이 문서는 실험 설계 지침이다. 설치된 PrimeSim 엔진의 수치 옵션이나 측정 구문을 검증 없이 제시하지 않는다. 현재 패키지의 SPICE 파일은 정상 기능 시험의 뼈대이며 아래 특성화용 완성 deck은 실제 환경에 맞춰 작성해야 한다.

## 0. 출발 조건

- 정상 DFF 기능, reset 비활성 조건, model corner, 전원/온도, well bias 확인.
- 재생 피드백 루프를 추적해 master/slave 노드 식별. 출력 버퍼 뒤 Q와 내부 slave 노드를 구별.
- 각 문턱(VIL/VIH)을 어떻게 정의했는지 기록. 임의의 0.2/0.8 VDD를 최종 정답으로 삼지 않는다. 다음 단의 입력 특성/라이브러리 기준과 일치시킨다.
- 동일 종류 DFF의 다음 단 입력을 실제 부하로 연결한다. TW1 측정은 특성화 1단+동일 부하용 DFF, TW2는 특성화 2단+동일 부하용 DFF를 기본으로 검토한다. 모든 DFF의 reset/well/power를 연결한다.
- interstage delay와 내부 RC를 포함한다. 버퍼, 배선, 분기 부하를 임의로 없애지 않는다.
- 초기 기준은 한 PVT, 한 duty, 하나의 충분히 긴 기준 주기. 논문의 800 ps를 이 공정의 정답으로 복사하지 않는다.

## 1. 자극과 오프셋

정상 안정 상태 이후 한 번의 D 전이를 CK의 첫 시험 rising edge 근처에 배치한다. t0는 CK 50% crossing, delta=tD50-tCK50. D 상승/하강을 각각 실험한다. CK/D slew 정의가 10-90%인지 0-100%인지 기록한다.

입력 time delay 숫자와 실제 파형의 crossing time은 같다고 가정하지 않는다. 파형에서 측정해 확인한다. 첫 포착 이후 불필요한 데이터 전이를 넣지 않는다.

## 2. 경계 탐색

1. 넓은 delta 범위의 coarse sweep으로 최종 high/low 경계와 관측 전압의 단조 구간을 찾는다.
2. 동일 관측 노드/시점에서 두 입력 offset의 전압이 문턱을 양쪽으로 감싸는 bracket을 확보한다.
3. `boundary.bisect_threshold(evaluate, low, high, threshold, tolerance)`를 각각 VIL 및 VIH에 적용한다. 함수는 증가/감소 양쪽을 지원한다. 여러 전이 구간이면 구간을 나누어 누락 없이 다룬다.
4. 반환하는 것은 경계 위치의 구간이다. VIL 경계 구간과 VIH 경계 구간의 차이로 window 폭의 최소/최대 범위를 계산한다. 단순 midpoint 값뿐 아니라 폭의 불확실성을 보관한다.
5. 폭이 수치 오차와 비슷하거나 두 경계 구간이 겹치면 추출 실패다. binary search 반복 수를 늘려 실제 정밀도를 얻었다고 주장하지 않는다.

같은 입력으로 반복한 실행의 차이, offset 표현 유효 자릿수, 내부 timestep, 전압 허용오차가 전부 영향을 준다. 단순 입력 sweep의 한계에 걸리면 초기 기준 주기를 조정하거나 참고문헌 [4]의 정밀 전파 방법 등을 추가 조사해야 한다. 현재 경계 함수는 그 논문의 알고리즘을 구현한 것이 아니다. 임의 초기조건만으로 얻은 장시간 metastability를 입력 확률 window로 대체하지 않는다.

## 3. tau_M / tau_S

해당 latch가 재생하는 위상에서 가까운 두 궤적의 전압 차이 delta_v(t)를 사용한다. 두 궤적의 시간축을 맞추고 초기 스위칭 transient, 공통모드 성분, 출력 포화 구간을 제외한다. master와 slave 각각 별도 구간을 선정한다.

단일 파형 V(t)-Vm을 쓰려면 Vm 결정 근거가 필요하다. 기본은 가까운 두 궤적의 차이를 권장하되, 두 궤적이 다른 동작 영역으로 나뉘지 않는지 확인한다. `analyze.py`는 CSV에 준비된 delta_v를 피팅하며 임의로 Vm이나 노드를 선택하지 않는다.

CSV 형식:
```csv
time_s,delta_v
```

호출 형식 (시간 값은 실제 선택 구간으로 대체):
```text
python scripts/analyze.py tau --csv results/master_delta.csv --start 1.1e-9 --stop 1.2e-9 --out results/tau_master_candidate.json
```

ln(abs(delta_v))=a+t/tau를 피팅한다. 양의 slope, 잔차, R2, 구간 변경 민감도, perturbation 크기 변경 민감도를 기록한다. 5점은 프로그램의 최소 조건일 뿐 충분한 물리 검증 기준이 아니다. 최소 세 개의 겹치는 fit 구간과 두 perturbation 크기를 비교하도록 실험을 구성한다.

## 4. TW1 / TW2

확인된 tau와 동일한 기준 조건에서 n=1,2의 관측 시각 t0+n*T에 대한 입력 window 폭을 추출한다. threshold 이름은 전압 기준, CSV의 low/high는 시간 순서다. 하강 입력일 때 전압 경계 순서와 시간 순서는 뒤집힐 수 있으므로 시간을 정렬한다.

CSV 형식:
```csv
paper_n,period_s,duty_high,delta_low_s,delta_high_s
```

```text
python scripts/analyze.py aperture --csv results/windows.csv --tau-master 실제초값 --tau-slave 실제초값 --out results/aperture_candidates.json
```

스크립트는 식 (18)을 행별로 계산한다. 서로 다른 PVT/방향/슬루/부하의 결과를 자동 평균하지 않는다. CSV의 경계 숫자는 반드시 원본 bracket과 실행 ID에 연결한다. TW 입력용 scalar 선정과 오차 범위는 검토 기록에 남긴다.

## 5. 수렴성과 독립 검증

최소한 기준 solver 설정과 더 엄격한 설정에서 동일 실험을 수행한다. 최대 내부 timestep, 정확도 옵션, waveform 저장 간격을 구분한다. 한 항목씩 바꿔 결과 민감도를 판단한다.

추천 초기 검토 기준 (논문에서 정한 기준이 아닌 본 프로젝트의 제안):
- window bracket 불확실성/폭 1% 이하 목표. 미달이면 원인과 결과 범위를 명시.
- 더 엄격한 solver 설정에서 tau 변화 5% 이하 및 계산 log10(MTBF/year) 변화 0.3 decade 이하 목표.
- 로그 MTBF는 tau 오차에 매우 민감하므로 tau 5% 통과만으로 승인하지 않는다.
- fit R2를 합격의 유일 기준으로 사용하지 않는다. 고정 임계값을 통과시키려 구간을 자의적으로 선택하지 않는다.

2/3/4 DFF 및 여러 주기에서 독립 검증한다. 같은 TW 추출 데이터를 식 (18)로 역산한 뒤 다시 대입한 결과는 독립 검증이 아니다.

가능한 관측 가능한 비교량:
- 적당한 주기에서 n번째 출력의 invalid window 직접 측정과 모델 window의 비교.
- 추가 DFF의 관측 시점에서 failure 정의에 따른 체인 실패 window 측정. 실제 metastability failure 정의와 연결되는 방식인지 명시한다.

주의: invalid voltage window 기반 값 자체도 실제 failure의 보수적 proxy일 수 있다. 이를 실측 MTBF 또는 ground truth라고 부르지 않는다. 식 (17)의 하한 성질을 실증하려면 비교 기준이 독립적이고 정의가 일치해야 한다. 직접 다단 window가 정밀도 한계 아래면 검증 불가로 기록한다. 긴 transient에서 실패가 한 번도 없었다고 큰 MTBF를 입증할 수 없다.

## 6. 배포용 파라미터

각 PVT/방향/슬루/부하 조건의 원시 추출값과 검증 기록을 보관한다. 더 나쁜 방향을 대표로 쓰는 경우 그 근거를 남긴다. tau와 TW의 오차가 연관되므로 각 값을 따로 worst로 뽑아 보수적이라고 단정하지 않는다. 재추출 세트별 MTBF의 민감도와 보수적 envelope를 검토한다.

검토자와 날짜, 증거 경로, 승인 범위가 있는 조건만 validated로 승격한다. 그 외는 candidate로 유지한다. 모델 적용 범위 밖의 duty/주기/단수는 외삽으로 표시하고 추천하지 않는다.
