import os
import whisper

model = whisper.load_model("base")

SUPPORTED_FORMATS = [".wav", ".mp3", ".m4a"]


def speech_to_text(audio_path):
    """
    Whisper 기반 음성 → 텍스트 변환 함수
    """

    # 1. 입력값 확인
    if not audio_path:
        return {
            "status": "error",
            "data": None,
            "error": {
                "code": "A_EMPTY_INPUT",
                "message": "음성 파일 경로가 없습니다."
            }
        }

    # 2. 파일 존재 여부 확인
    if not os.path.exists(audio_path):
        return {
            "status": "error",
            "data": None,
            "error": {
                "code": "A_AUDIO_FILE_NOT_FOUND",
                "message": "음성 파일을 찾을 수 없습니다."
            }
        }

    # 3. 파일 형식 확인
    ext = os.path.splitext(audio_path)[1].lower()

    if ext not in SUPPORTED_FORMATS:
        return {
            "status": "error",
            "data": None,
            "error": {
                "code": "A_UNSUPPORTED_AUDIO_FORMAT",
                "message": "지원하지 않는 음성 파일 형식입니다."
            }
        }

    # 4. Whisper 음성 인식
    try:
        result = model.transcribe(audio_path)

        recognized_text = result["text"].strip()

        return {
            "status": "success",
            "data": {
                "recognized_text": recognized_text,
                "input_type": "audio",
                "audio_path": audio_path
            },
            "error": None
        }

    # 5. 예외 처리
    except Exception:
        return {
            "status": "error",
            "data": None,
            "error": {
                "code": "A_STT_FAILED",
                "message": "음성 인식에 실패했습니다."
            }
        }


# 단독 실행 테스트
if __name__ == "__main__":

    test_audio = "module_a/sample_audio/test.wav"

    response = speech_to_text(test_audio)

    print(response)
