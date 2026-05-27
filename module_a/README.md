# Module A - 음성 입력 및 음성 인식 모듈

## 기능

- 음성 파일 입력
- Whisper 기반 음성 인식
- 음성 → 텍스트 변환
- Module B 전달용 JSON 생성

## 실행 방법

```bash
python module_a/speech_to_text.py

---

## 입력값 형식

```python
speech_to_text(audio_path)
```

| 값 | 설명 |
|---|---|
| audio_path | 음성 파일 경로 |

---

## 반환값 예시

```json
{
  "status": "success",
  "data": {
    "recognized_text": "서울역에서 숙대입구역까지 가고 싶어요",
    "input_type": "audio",
    "audio_path": "module_a/sample_audio/test.wav"
  },
  "error": null
}
```

---

## ffmpeg 설치 안내

Whisper 사용을 위해 ffmpeg 설치가 필요할 수 있음.

Windows 설치 예시:

```bash
winget install ffmpeg
```
