# oss_project_team36_gildongmu

## 프로젝트명

길동무

## 프로젝트 소개

길동무는 노인 교통약자의 대중교통 이용을 돕기 위한 음성 기반 길 안내 도우미입니다.

사용자가 음성 또는 텍스트로 이동 요청을 입력하면, 시스템이 입력 내용을 분석해 출발지와 목적지를 파악하고 이동 경로를 안내합니다. 복잡한 교통 앱 조작이 어려운 사용자를 위해, 자연어 기반 입력과 간단한 안내 흐름을 중심으로 설계했습니다.

본 프로젝트는 최종 상용 서비스 수준의 UI/UX 구현보다는, 계획서에서 제시한 음성 기반 길 안내 서비스의 핵심 기능이 실제로 연결되는지 확인하는 프로토타입 단계입니다. 음성 인식, 장소·의도 분석, 경로 판단, 안내문 생성, 음성 출력까지 이어지는 전체 파이프라인의 초석을 만드는 것을 목표로 했습니다.

## 개발 배경

노인 교통약자는 대중교통 이용 과정에서 출발지와 목적지 입력, 환승 정보 확인, 막차 여부 확인, 대체 이동수단 판단 등에 어려움을 겪을 수 있습니다.

길동무는 이러한 문제를 해결하기 위해 사용자가 직접 복잡한 지도 앱을 조작하지 않아도, 음성이나 간단한 문장 입력만으로 이동 안내를 받을 수 있는 구조를 제안합니다.

## 주요 기능

* 음성 입력을 통한 길 안내 요청
* Whisper 기반 음성-텍스트 변환
* 텍스트 기반 경로 요청
* 출발지와 목적지 추출
* 사용자 의도 분석
* 대중교통 경로 판단
* ODsay API 기반 경로 조회
* API 실패 시 CSV 기반 fallback 처리
* 노인 친화형 안내문 생성
* gTTS 기반 음성 안내 출력
* Gradio 기반 프로토타입 UI 제공

## 전체 동작 흐름

```text
사용자 음성/텍스트 입력
        ↓
Module A: 음성 인식 및 텍스트 변환
        ↓
Module B: 장소 추출, 의도 분석, 경로 판단
        ↓
Module C: 안내문 생성 및 음성 출력
        ↓
Module C: Gradio UI에서 안내 결과 제공
```

## 팀원 역할

* 김유진: Module A. 음성 입력 및 음성 인식 모듈
* 양이진하: Module B. 장소 추출, 의도 분류, 교통 경로 판단 모듈
* 이예원: Module C. 안내문 생성, 음성 출력 및 UI 통합 모듈

## 모듈 설명

### Module A. 음성 인식 모듈

사용자의 음성 입력을 받아 Whisper 모델을 통해 텍스트로 변환합니다. 변환된 텍스트는 Module B에서 분석할 수 있는 구조로 전달됩니다.

### Module B. 경로 분석 모듈

입력 문장에서 출발지, 목적지, 사용자 의도를 분석합니다.
BERT 기반 의도 분류와 장소 추출 NER 모델을 활용했으며, 음성 인식 과정에서 발생할 수 있는 역명 오인식 문제를 일부 보완했습니다.

예시:

```text
사울약 → 서울역
숙대입고 → 숙대입구역
강남약 → 강남역
```

또한 ODsay API를 통한 경로 조회를 시도하고, API 호출이 어려운 경우 CSV 기반 fallback 데이터를 활용합니다.

### Module C. 안내문 생성 및 음성 출력 모듈

Module B의 분석 결과를 바탕으로 사용자가 이해하기 쉬운 안내문을 생성합니다. 생성된 안내문은 화면에 표시되며, gTTS를 통해 음성 안내로도 출력됩니다.

## 폴더 구조

```text
oss_project_team36_gildongmu/
├── app.py
├── requirements.txt
├── integration_rule.md
├── docs/
├── module_a/
│   └── speech_to_text.py
├── module_b/
│   ├── route_ai_analyzer.py
│   ├── realtime_transport_api.py
│   ├── predict_bert_intent.py
│   ├── predict_location_ner.py
│   ├── train_location_ner.py
│   ├── stations.csv
│   ├── data/
│   └── models/
└── module_c/
    ├── guide_generator.py
    └── text_to_speech.py
```

## 실행 방법

```bash
git clone https://github.com/Jinnhaa/oss_project_team36_gildongmu.git
cd oss_project_team36_gildongmu
```

모델 파일은 Git LFS로 관리됩니다.

```bash
git lfs install
git lfs pull
```

필요한 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

ODsay API를 사용하는 경우 로컬 환경변수로 API Key를 설정합니다.

```bash
export ODSAY_API_KEY="발급받은 ODsay API Key"
```

앱을 실행합니다.

```bash
PYTHONPATH=. python3 app.py
```

실행 후 브라우저에서 아래 주소로 접속합니다.

```text
http://127.0.0.1:7860
```

## 데모 문장 예시

```text
서울역에서 출발해서 숙대입구역까지 가고 싶어요
```

```text
사울약에서 숙대입고까지 가고 싶어
```

```text
오늘 점심 뭐 먹지?
```

## 프로젝트 의의

본 프로젝트는 노인 교통약자를 위한 완성형 서비스라기보다는, 음성 기반 길 안내 서비스가 실제로 구현 가능한지 확인하기 위한 기능 중심 프로토타입입니다.

음성 인식, 자연어 분석, 경로 판단, 안내문 생성, 음성 출력 기능을 하나의 흐름으로 연결함으로써 향후 사용자 친화적인 UI/UX 개선과 실제 교통 데이터 연동을 확장할 수 있는 기반을 마련했습니다.
