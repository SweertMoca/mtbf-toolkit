# 모델과 적용 범위

근거: Beer, Cox, Chaney, Zar, ASYNC 2013, DOI 10.1109/ASYNC.2013.18. 원 논문의 수식을 기준으로 한다. 논문 파일은 이 패키지에 포함하지 않는다. 인쇄 페이지 162~163의 식 (9), (17), (18), (19)를 구현한다.

## 변수와 수식

- K: 실제 동기화 체인의 DFF 개수. 이 구현은 K>=2.
- n=K-1: 식 (17)의 보수적 모델에서 해소 시간을 인정하는 단계 수. 마지막 DFF의 추가 해소 시간은 계산에 넣지 않는다. 이후 수신 로직의 FF는 K에 자동 포함하지 않는다.
- T=1/fC. fC는 수신 클록 Hz, fD는 비동기 입력의 초당 전이 횟수. 송신 클록 주파수를 그대로 fD로 대입하지 않는다.
- alpha: 상승 에지 master–slave 구조에서 CK HIGH 비율. 다른 구조/극성은 검증 없이 적용하지 않는다.
- 모든 시간은 초, 전압 V, 주파수 Hz. 1년=365.25*86400초.

```text
1/tau_eff = alpha/tau_M + (1-alpha)/tau_S                 (9)
TW(n) = TW1 * (TW2/TW1)^(n-1)                            (19)
MTBF_lower(K) = exp(n*T/tau_eff)/(TW(n)*fD*fC), n=K-1     (17)
ln TW(n) = ln(delta_high-delta_low) + n*T/tau_eff          (18)
```

式 (18)의 관측은 입력 첫 포착 에지를 t=0으로 할 때 n번째 특성화 단계의 slave 출력에서 t=n*T를 기준으로 한다. 실제 시뮬레이션에서는 t0+n*T. 그 시점의 다음 클록 에지와 측정 순서/보간 정의를 명시한다. t=n*T-epsilon에서 샘플링한다면 같은 수식을 그대로 적용하지 말고 시간 이동이 계수에 미치는 영향을 포함하고 기준을 일치시킨다.

TW1/TW2는 보통 setup/hold 데이터에서 얻는 값이 아니다. 동일 부하/문턱/슬루/PVT 조건으로 특성화해야 한다. 식 (19)는 동일 단계와 일관된 최종 전압 범위에 대한 관계다.

계산은 로그 공간에서 진행한다. 단계를 추가할 때 로그 MTBF 증가량은 T/tau_eff - ln(TW2/TW1)이다. 무조건 증가한다고 코드에 가정하지 않는다.

## 가정 및 한계

동일한 master–slave DFF, 동일 수신 클록, 단계 사이 조합논리 없음, 특성화와 일치하는 부하/배선, 유효한 최소 클록 펄스 폭, 모델의 지수 해소 구간이 필요하다. 비동기 입력의 상대 위상은 논문의 균일 분포 가정을 따른다. 관련 클록/위상이 집중된 입력에 대해서는 별도 검토한다.

실제 M/X 선언 및 모델 해석, 저장 노드, 정상 기능은 대상 회로에서 검증해야 한다.

한 PVT에서 얻은 값을 다른 PVT에 복사하지 않는다. duty 변경이 tau_eff에 반영되더라도 TW의 재사용 가능 범위는 실험으로 확인한다. 최소 펄스 폭이 깨지는 영역은 제외한다. 논문 그림 8도 이런 한계를 보인다.

rise/fall 방향은 각각 추출한다. 전체 전이율 fD를 사용해 더 불리한 방향의 하한을 적용하면 보수적으로 평가할 수 있다. 방향별 전이율로 합산하려면 failure rate 단위로 결합하며 두 MTBF를 산술 평균하지 않는다.

현재 도구는 한 체인 모델이다. 칩 전체 목표는 여러 CDC 체인의 고장률 예산 배분이 추가로 필요하다. 또한 pulse 유실, multi-bit coherency, reset CDC, 프로토콜 오류는 이 MTBF만으로 해결되지 않는다.

## 추천 제한

parameters.status=validated, validated_scope의 clock_hz/duty_high 범위, condition_id, slew, load_id, interconnect_id, max_dffs가 모두 맞아야 추천한다. 이 상태 표시는 사용자가 제공하는 검토 기록에 의존하며 프로그램이 물리적 보증을 인증하는 기능은 아니다.

validated_scope 예시 구조 (아래 값은 형식 예시이며 실측값이 아님):
```json
{
  "clock_hz": [800000000, 1000000000],
  "duty_high": [0.5, 0.5],
  "condition_id": "CELL_CORNER_VOLT_TEMP_EDGE_REVIEW_ID",
  "input_slew_s": 2e-11,
  "clock_slew_s": 2e-11,
  "load_id": "verified_load_description",
  "interconnect_id": "verified_interconnect_description",
  "max_dffs": 4
}
```

모델 하한이 목표 미만이면 목표 충족을 입증하지 못한 것이며 실제 MTBF가 반드시 부족하다는 뜻은 아니다.
