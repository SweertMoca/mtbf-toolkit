"""Build a readable, offline copy/paste package. No network or simulator access."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'github_publish'
OUT.mkdir(exist_ok=True)
names = [
    'START_HERE.md', 'WORK_PC_AGENT.md', 'THEORY_AND_CONVENTIONS.md',
    'CHARACTERIZATION_PROTOCOL.md', 'RESULT_REVIEW.md',
    'scripts/mtbf.py', 'scripts/inspect_netlist.py', 'scripts/check_environment.py',
    'scripts/run_case.py', 'scripts/analyze.py', 'scripts/boundary.py',
    'tests/test_tools.py', 'config/application.example.json',
    'config/parameters.synthetic.json', 'config/run.example.json',
    'templates/nominal_check.sp.in',
]
files = {}
for name in names:
    content = (ROOT / name).read_text(encoding='utf-8')
    # Export reusable material only. No photos, PDF, runtime logs, or cell identifiers.
    content = content.replace('DFFRPQLV_D1_N_M7P5TL_C60L08_nominal_max_25c.spice', 'YOUR_DFF_NETLIST.spice')
    content = content.replace('DFFRPQLV_D1_N_M7P5TL_C60L08', 'YOUR_DFF_CELL')
    content = content.replace('REPLACE_WITH_ABSOLUTE_CELL_NETLIST_PATH', 'REPLACE_WITH_ABSOLUTE_CELL_NETLIST_PATH')
    content = content.replace('사진에는 transistor 단자 연결 주석과 기생 RC가 확인되지만, 실제 M/X 선언 및 모델 해석, 저장 노드, 정상 기능은 아직 검증되지 않았다. s0는 후보일 뿐이다.',
                              '실제 M/X 선언 및 모델 해석, 저장 노드, 정상 기능은 대상 회로에서 검증해야 한다.')
    content = content.replace('외부 핀 CK D Q R VDD VNW VPW VSS는 사진에서 전사한 정보다.',
                              '외부 핀 CK D Q R VDD VNW VPW VSS는 템플릿의 예시다.')
    content = content.replace('Pin order below transcribed from photographs; verify against actual .SUBCKT.',
                              'Pin order below is an example; replace using the actual .SUBCKT.')
    content = content.replace('폴더의 MTBF_bounds_for_multistage_synchronizers.pdf, ', '')
    content = content.replace('PDF 전체를 읽고 수식을 이미지로 확인했다.', '원 논문의 수식을 기준으로 한다. 논문 파일은 이 패키지에 포함하지 않는다.')
    content = content.replace('results/demo_001', 'results/demo_001')
    files[name] = content
payload = json.dumps(files, ensure_ascii=False, indent=2)
hashes = {name: hashlib.sha256(content.encode('utf-8')).hexdigest() for name, content in files.items()}
header = '''# -*- coding: utf-8 -*-
"""Offline MTBF toolkit installer. Python 3.9+; standard library only.
Copy the entire GitHub Raw file into bootstrap_mtbf.py, then run:
    python bootstrap_mtbf.py --dest mtbf_work
This writes bundled text files only. It does not run a simulator, install
dependencies, download anything, or overwrite an existing destination.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

'''
# JSON strings are valid Python strings, so embed a plain, readable dictionary.
body = 'FILES = ' + payload + '\n\nSHA256 = ' + json.dumps(hashes, indent=2) + '\n'
tail = '''

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', default='mtbf_work')
    args = parser.parse_args()
    dest = Path(args.dest).resolve()
    for name, content in FILES.items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or '\\\\' in name or ':' in name:
            raise SystemExit('Unsafe bundled path: ' + name)
        if hashlib.sha256(content.encode('utf-8')).hexdigest() != SHA256[name]:
            raise SystemExit('Copy integrity check failed: ' + name)
    if dest.exists():
        raise SystemExit('Destination already exists; use a NEW --dest directory: ' + str(dest))
    dest.mkdir(parents=True, exist_ok=False)
    for name, content in FILES.items():
        path = dest.joinpath(*PurePosixPath(name).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x', encoding='utf-8', newline='\\n') as stream:
            stream.write(content)
        if hashlib.sha256(path.read_bytes()).hexdigest() != SHA256[name]:
            raise SystemExit('Written file verification failed: ' + name)
    (dest / 'results').mkdir()
    (dest / 'BUNDLE_MANIFEST.json').write_text(json.dumps(SHA256, indent=2), encoding='utf-8')
    print('Created and verified', len(FILES), 'files in', dest)
    print('Next: open START_HERE.md and give WORK_PC_AGENT.md to Copilot.')
    print('Run tests from that folder: python -m unittest discover -s tests -v')


if __name__ == '__main__':
    main()
'''
(OUT / 'COPY_THIS_bootstrap.py').write_text(header + body + tail, encoding='utf-8', newline='\n')
readme = '''# MTBF Toolkit — 웹에서 복사해서 사용하기

Python 표준 라이브러리만 사용하는 논문 기반 MTBF 계산·특성화 보조 도구입니다.
실제 셀 특성값과 PrimeSim 연결은 업무용 환경에서 확인해야 합니다.
예제 파라미터는 가상 값이며 설계 판단에 사용할 수 없습니다.

## 업무용 PC에서 하는 일

1. 이 저장소에서 **COPY_THIS_bootstrap.py**를 엽니다.
2. **Raw** 버튼을 누릅니다. Raw 화면에서 `Ctrl+A`, `Ctrl+C`로 전체 내용을 복사합니다.
3. 업무용 VS Code에서 새 파일 `bootstrap_mtbf.py`를 만들고 붙여 넣은 뒤 UTF-8로 저장합니다.
4. 그 파일이 있는 폴더의 터미널에서 실행합니다.

```text
python bootstrap_mtbf.py --dest mtbf_work
```

Python 실행 명령이 다르면 확인된 `python3`, `py -3` 또는 실행 파일 경로로 바꿉니다.
`mtbf_work`가 이미 있으면 다른 새 폴더명을 사용하세요. 기존 폴더는 덮어쓰지 않습니다.
성공 시 **Created and verified 16 files**가 표시됩니다.
설치기는 네트워크 접속, 프로그램 설치, PrimeSim 실행을 하지 않고 파일만 생성합니다.

5. VS Code에서 생성된 **mtbf_work** 폴더를 엽니다.
6. Copilot에 아래 요청을 붙여 넣습니다.

```text
START_HERE.md와 WORK_PC_AGENT.md를 읽고 단계 A와 B를 수행해줘.
실제 대상 DFF 넷리스트와 PDK 경로는 필요한 경우 나에게 물어봐.
YOUR_DFF_NETLIST.spice와 YOUR_DFF_CELL은 예시이므로 실제 파일과 셀 이름으로 설정해.
핀, reset, well bias, 전압, 모델 코너, PrimeSim 명령은 확인된 자료를 사용해.
가능한 검사는 직접 실행하고, 실행 권한이 없으면 정확한 명령을 알려줘.
결과는 results/work_pc_001에 저장하고 RETURN_TO_REVIEWER.md를 작성해줘.
아직 실제 파라미터를 검증하지 않았으므로 DFF 개수를 추천하지 마.
```

## 생성되는 내용

- MTBF 계산기: 논문 식 (9), (17), (19), 실제 DFF 개수 K와 N=K-1 구분
- 넷리스트·환경 검사, 외부 시뮬레이터 실행 기록
- 지수 파형 피팅, aperture 환산, bracket 탐색 함수
- Copilot 실행 지침, 특성화 절차, 결과 반환 양식
- 자동 테스트 12개

검증되지 않은 파라미터와 적용 범위 밖 조건은 추천에서 제외합니다.
PrimeSim 어댑터 및 실제 회로 검증은 아직 대상 환경에 연결해야 합니다.

원 논문: Beer et al., “MTBF Bounds for Multistage Synchronizers”, ASYNC 2013,
DOI: 10.1109/ASYNC.2013.18.
이 전달 파일에는 PDK, 실제 넷리스트, 사진, 논문 PDF, 로컬 실행 로그가 없습니다.
'''
(OUT / 'README.md').write_text(readme, encoding='utf-8', newline='\n')
print('Created GitHub delivery files in', OUT)


if __name__ == '__main__':
    pass
