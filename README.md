# oss_project_team36_gildongmu
Open-source AI based mobile voice navigation assistant for elderly public transportation users.

## 팀명
길동무

## 프로젝트 소개
오픈소스 AI 기반 노인 교통약자를 위한 모바일형 음성 길 안내 도우미 프로젝트입니다.

## 주요 기능
- Whisper 기반 음성-텍스트 변환
- Sentence-Transformers 기반 장소·의도 분석
- 샘플 교통 데이터 기반 이동 가능 여부 판단
- 노인 친화형 안내문 생성 및 음성 출력
- 모바일형 인터페이스 프로토타입 구현

## 팀원 역할
- 김유진: Module A. 음성 입력 및 음성 인식 모듈
- 양이진하: Module B. 장소·의도 분석 및 교통 판단 모듈
- 이예원: Module C. 안내문 생성, 음성 출력 및 모바일형 인터페이스 모듈

## 폴더 구조
```text
gildongmu-ai/
 ├─ app.py
 ├─ speech_to_text.py
 ├─ route_ai_analyzer.py
 ├─ guide_generator.py
 ├─ text_to_speech.py
 ├─ data/
 ├─ tests/
 ├─ sample_audio/
 ├─ screenshots/
 └─ docs/
