import os
from gtts import gTTS


def text_to_speech(c_result: dict) -> dict:
    """guide_generator 결과를 받아 voice_text를 MP3로 저장한다."""
    try:
        if not c_result or c_result.get("status") == "error":
            return _error_response("C_TTS_FAILED", "음성 출력할 안내문이 없습니다.")

        data = c_result.get("data", {})
        voice_text = data.get("voice_text", "").strip()

        if not voice_text:
            return _error_response("C_TTS_FAILED", "음성 출력할 텍스트가 없습니다.")

        output_path = data.get("tts_file_path", "outputs/voice/voice_guide.mp3")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        tts = gTTS(text=voice_text, lang="ko", slow=True)
        tts.save(output_path)

        return {
            "status": "success",
            "data": {**data, "tts_file_path": output_path},
            "error": None,
        }

    except Exception:
        return _error_response("C_TTS_FAILED", "음성 파일 생성 중 오류가 발생했습니다.")


def _error_response(code: str, message: str) -> dict:
    return {
        "status": "error",
        "data": None,
        "error": {
            "code": code,
            "message": message,
        },
    }
