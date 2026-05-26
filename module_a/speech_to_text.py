import whisper

model = whisper.load_model("base")

audio_path = "module_a/sample_audio/test.wav"

result = model.transcribe(audio_path)

recognized_text = result["text"]

response = {
    "status": "success",
    "data": {
        "recognized_text": recognized_text
    },
    "error": None
}

print(response)