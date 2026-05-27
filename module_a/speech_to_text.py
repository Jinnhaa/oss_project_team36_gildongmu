import os
import whisper

model = whisper.load_model("base")

SUPPORTED_FORMATS = [".wav", ".mp3", ".m4a"]


def speech_to_text(audio_path):
    """
    Whisper 기반 음성 → 텍스트 변환 함수
    """

    # 입력값 확인
    if not audio_path:
        return {
            "status": "error",
            "data": None,
            "error": {
                "code": "A_EMPTY_INPUT",
                "message": "음성 파일 경로가 없습니다."
            }
        }

    # 파일 존재 여부 확인
    if not os.path.exists(audio_path):
        return {
            "status": "error",
            "data": None,
            "error": {
                "code": "A_AUDIO_FILE_NOT_FOUND",
                "message": "음성 파일을 찾을 수 없습니다."
            }
        }

    # 파일 형식 확인
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

    # Whisper STT 수행
    try:
        result = model.transcribe(audio_path)

        recognized_text = result["text"].strip()

        # 빈 결과 처리
        if not recognized_text:
            return {
                "status": "error",
                "data": None,
                "error": {
                    "code": "A_STT_FAILED",
                    "message": "음성 인식 결과가 비어 있습니다."
                }
            }

        return {
            "status": "success",
            "data": {
                "recognized_text": recognized_text,
                "input_type": "audio",
                "audio_path": audio_path
            },
            "error": None
        }

    except Exception:
        return {
            "status": "error",
            "data": None,
            "error": {
                "code": "A_STT_FAILED",
                "message": "음성 인식에 실패했습니다."
            }
        }


def process_input(audio_path=None, text=None):
    """
    app.py 통합 실행용 wrapper 함수
    """

    # 텍스트 직접 입력 처리
    if text:

        cleaned_text = text.strip()

        if not cleaned_text:
            return {
                "status": "error",
                "data": None,
                "error": {
                    "code": "A_EMPTY_INPUT",
                    "message": "텍스트 입력이 비어 있습니다."
                }
            }

        return {
            "status": "success",
            "data": {
                "recognized_text": cleaned_text,
                "input_type": "text",
                "audio_path": None
            },
            "error": None
        }

    # 음성 입력 처리
    return speech_to_text(audio_path)


# 단독 실행 테스트
if __name__ == "__main__":

    test_audio = "module_a/sample_audio/test.wav"

    response = process_input(audio_path=test_audio)

    print(response)
