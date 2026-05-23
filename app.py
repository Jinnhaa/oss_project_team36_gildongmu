import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from module_b.route_ai_analyzer import analyze_route
from module_c.guide_generator import generate_guide
from module_c.text_to_speech import text_to_speech

try:
    from module_a.speech_to_text import process_input as stt_process
    HAS_MODULE_A = True
except ImportError:
    HAS_MODULE_A = False


BG_COLOR     = "#FFFDE7"
HEADER_COLOR = "#F9A825"
TEXT_COLOR   = "#212121"
ERROR_COLOR  = "#E53935"

DEFAULT_FONT = 20
MIN_FONT     = 14
MAX_FONT     = 32


# ── HTML 렌더 ─────────────────────────────────────────────────────────────

def render_html(data: dict, font_size: int) -> str:
    title      = data.get("title", "")
    summary    = data.get("summary_message", "")
    steps      = data.get("guide_steps", [])
    steps_html = "".join(f"<li>{s}</li>" for s in steps)

    return f"""
    <div style="font-family:sans-serif; padding:20px; max-width:480px; margin:0 auto;
                background:{BG_COLOR}; border-radius:16px;">
        <div style="background:{HEADER_COLOR}; color:{TEXT_COLOR}; border-radius:12px;
                    padding:18px 22px; margin-bottom:16px;">
            <div style="font-size:{font_size + 6}px; font-weight:bold;">{title}</div>
            <div style="font-size:{font_size - 2}px; margin-top:8px;">{summary}</div>
        </div>
        <ol style="font-size:{font_size}px; line-height:2; padding-left:24px;
                   margin:0; color:{TEXT_COLOR};">
            {steps_html}
        </ol>
    </div>
    """


def render_error(message: str, font_size: int) -> str:
    return f"""
    <div style="font-family:sans-serif; padding:20px; max-width:480px; margin:0 auto;
                background:{BG_COLOR}; border-radius:16px;">
        <div style="background:{ERROR_COLOR}; color:white; border-radius:12px; padding:18px 22px;">
            <div style="font-size:{font_size + 2}px; font-weight:bold;">안내를 드리기 어려워요</div>
            <div style="font-size:{font_size - 2}px; margin-top:8px; opacity:0.9;">{message}</div>
        </div>
    </div>
    """


# ── 파이프라인 ────────────────────────────────────────────────────────────

def run_pipeline(text_input: str, audio_input, font_size: int):
    if audio_input and HAS_MODULE_A:
        a_result = stt_process({
            "input_type": "audio",
            "audio_path": audio_input,
            "text": None,
        })
    else:
        if not text_input or not text_input.strip():
            return render_error("입력값이 없습니다. 목적지를 말씀하거나 입력해 주세요.", font_size), None, None
        a_result = {
            "status": "success",
            "data": {
                "recognized_text": text_input.strip(),
                "input_type": "text",
                "audio_path": None,
            },
            "error": None,
        }

    if a_result["status"] == "error":
        return render_error(a_result["error"]["message"], font_size), None, None

    b_result = analyze_route(a_result)
    if b_result["status"] == "error":
        return render_error(b_result["error"]["message"], font_size), None, None

    c_result = generate_guide(b_result)
    if c_result["status"] == "error":
        return render_error(c_result["error"]["message"], font_size), None, None

    c_result  = text_to_speech(c_result)
    data      = c_result.get("data") if c_result["status"] == "success" else None

    if not data:
        return render_error("안내문 생성에 실패했습니다.", font_size), None, None

    tts_path  = data.get("tts_file_path")
    audio_out = tts_path if tts_path and os.path.exists(tts_path) else None

    return render_html(data, font_size), audio_out, data


def update_font(data, font_size: int):
    if data is None:
        return gr.update()
    return render_html(data, font_size)


def replay_audio(tts_path):
    if tts_path and os.path.exists(tts_path):
        return tts_path
    return None


# ── Gradio UI ─────────────────────────────────────────────────────────────

with gr.Blocks(title="길동무") as app:

    font_size_state = gr.State(value=DEFAULT_FONT)
    data_state      = gr.State(value=None)
    tts_path_state  = gr.State(value=None)

    with gr.Row():
        with gr.Column(scale=4):
            gr.Markdown(
                """
                <div style="padding:12px 0;">
                    <span style="font-size:32px; font-weight:bold;">🧭 길동무</span><br>
                    <span style="font-size:16px; color:#555;">노인 교통약자를 위한 음성 길 안내 도우미</span>
                </div>
                """
            )
        with gr.Column(scale=1):
            with gr.Accordion("⚙️", open=False):
                font_slider = gr.Slider(
                    minimum=MIN_FONT,
                    maximum=MAX_FONT,
                    value=DEFAULT_FONT,
                    step=2,
                    label="글자 크기",
                )

    text_box = gr.Textbox(
        placeholder="예: 서울역에서 숙대입구역까지 가고 싶어요",
        label="어디까지 가시나요?",
        lines=2,
    )

    if HAS_MODULE_A:
        audio_box = gr.Audio(sources=["microphone"], type="filepath", label="음성으로 말씀해 주세요")
    else:
        audio_box = gr.State(value=None)

    btn = gr.Button("안내 받기", variant="primary", size="lg")

    guide_output = gr.HTML(label="안내 결과")

    with gr.Row():
        audio_output = gr.Audio(label="음성 안내", autoplay=True, scale=4)
        btn_replay   = gr.Button("🔊 다시 듣기", size="lg", scale=1)

    # 안내 받기
    btn.click(
        fn=run_pipeline,
        inputs=[text_box, audio_box, font_size_state],
        outputs=[guide_output, audio_output, data_state],
    )
    text_box.submit(
        fn=run_pipeline,
        inputs=[text_box, audio_box, font_size_state],
        outputs=[guide_output, audio_output, data_state],
    )

    # 다시 듣기
    btn_replay.click(
        fn=replay_audio,
        inputs=[tts_path_state],
        outputs=[audio_output],
    )

    # 글자 크기 조절
    font_slider.change(
        fn=update_font,
        inputs=[data_state, font_slider],
        outputs=[guide_output],
    )
    font_slider.change(
        fn=lambda fs: fs,
        inputs=[font_slider],
        outputs=[font_size_state],
    )

if __name__ == "__main__":
    app.launch(theme=gr.themes.Soft())
