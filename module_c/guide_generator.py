def generate_guide(b_result: dict) -> dict:
    """Module B 결과를 받아 노인 친화 안내문을 생성한다."""
    try:
        if not b_result:
            return _error_response("C_EMPTY_ROUTE_RESULT", "경로 분석 결과가 없습니다.")

        if b_result.get("status") == "error":
            return _error_response("C_EMPTY_ROUTE_RESULT", "경로를 찾을 수 없습니다. 다시 말씀해 주세요.")

        data = b_result.get("data")
        if not data:
            return _error_response("C_EMPTY_ROUTE_RESULT", "경로 분석 결과가 없습니다.")

        scenario = data.get("scenario", "unknown")

        handlers = {
            "subway_available": _guide_subway_available,
            "last_train_ended": _guide_last_train_ended,
            "bus_alternative":  _guide_bus_alternative,
            "walking_needed":   _guide_walking_needed,
            "need_more_info":   _guide_need_more_info,
        }

        handler = handlers.get(scenario, _guide_unknown)
        return handler(data)

    except Exception:
        return _error_response("C_GUIDE_GENERATION_FAILED", "안내문 생성 중 오류가 발생했습니다.")


# ── 시나리오별 안내문 생성 ──────────────────────────────────────────────────

def _guide_subway_available(data: dict) -> dict:
    start       = data.get("start", "출발지")
    destination = data.get("destination", "목적지")
    summary     = data.get("route_summary", {})
    time_       = summary.get("estimated_time", "알 수 없음")
    transfer    = summary.get("transfer", "")

    steps = [
        f"{start}에서 지하철을 타세요.",
        f"{destination}에서 내리세요.",
        f"예상 이동 시간은 {time_}입니다.",
    ]
    if transfer and transfer != "환승 없음":
        steps.insert(2, f"{transfer}.")

    return _success_response(
        title=f"지하철로 이동할 수 있어요",
        summary_message=f"{start}에서 {destination}까지 지하철로 이동할 수 있습니다.",
        guide_steps=steps,
        voice_text=f"{start}에서 {destination}까지 지하철로 이동할 수 있습니다. " + " ".join(steps),
        screen_type="route_available",
    )


def _guide_last_train_ended(data: dict) -> dict:
    destination = data.get("destination", "목적지")

    return _success_response(
        title="막차가 끝났어요",
        summary_message=f"죄송합니다. {destination} 방향 막차가 끝났습니다.",
        guide_steps=[
            "오늘 막차는 이미 출발했습니다.",
            "택시나 버스 등 다른 교통수단을 이용해 보세요.",
        ],
        voice_text=f"죄송합니다. {destination} 방향 막차가 끝났습니다. 오늘 막차는 이미 출발했습니다. 택시나 버스 등 다른 교통수단을 이용해 보세요.",
        screen_type="last_train_ended",
    )


def _guide_bus_alternative(data: dict) -> dict:
    start       = data.get("start", "출발지")
    destination = data.get("destination", "목적지")
    summary     = data.get("route_summary", {})
    time_       = summary.get("estimated_time", "알 수 없음")

    return _success_response(
        title="버스로 이동할 수 있어요",
        summary_message=f"{start}에서 {destination}까지 버스로 이동할 수 있습니다.",
        guide_steps=[
            f"{start}에서 버스를 타세요.",
            f"{destination}에서 내리세요.",
            f"예상 이동 시간은 {time_}입니다.",
        ],
        voice_text=f"{start}에서 {destination}까지 버스로 이동할 수 있습니다. {start}에서 버스를 타세요. {destination}에서 내리세요. 예상 이동 시간은 {time_}입니다.",
        screen_type="alternative_route",
    )


def _guide_walking_needed(data: dict) -> dict:
    start       = data.get("start", "출발지")
    destination = data.get("destination", "목적지")
    summary     = data.get("route_summary", {})
    time_       = summary.get("estimated_time", "알 수 없음")

    return _success_response(
        title="걸어서 이동할 수 있어요",
        summary_message=f"{start}에서 {destination}까지 걸어서 이동할 수 있습니다.",
        guide_steps=[
            f"{start}에서 걸어서 출발하세요.",
            f"{destination}까지 이동하세요.",
            f"예상 이동 시간은 {time_}입니다.",
        ],
        voice_text=f"{start}에서 {destination}까지 걸어서 이동할 수 있습니다. {start}에서 걸어서 출발하세요. {destination}까지 이동하세요. 예상 이동 시간은 {time_}입니다.",
        screen_type="alternative_route",
    )


def _guide_need_more_info(data: dict) -> dict:
    return _success_response(
        title="조금 더 알려주세요",
        summary_message="출발지나 목적지를 정확히 말씀해 주세요.",
        guide_steps=[
            "어디서 출발하시나요?",
            "어디까지 가시나요?",
            "다시 한 번 말씀해 주세요.",
        ],
        voice_text="출발지나 목적지를 정확히 말씀해 주세요. 다시 한 번 말씀해 주세요.",
        screen_type="need_more_info",
    )


def _guide_unknown(data: dict) -> dict:
    return _success_response(
        title="안내를 드리기 어려워요",
        summary_message="죄송합니다. 경로를 찾을 수 없습니다.",
        guide_steps=[
            "요청하신 경로를 찾을 수 없습니다.",
            "다시 한 번 말씀해 주세요.",
        ],
        voice_text="죄송합니다. 경로를 찾을 수 없습니다. 다시 한 번 말씀해 주세요.",
        screen_type="error",
    )


# ── 응답 헬퍼 ─────────────────────────────────────────────────────────────

def _success_response(title, summary_message, guide_steps, voice_text, screen_type) -> dict:
    return {
        "status": "success",
        "data": {
            "title": title,
            "summary_message": summary_message,
            "guide_steps": guide_steps,
            "voice_text": voice_text,
            "screen_type": screen_type,
            "tts_file_path": "outputs/voice/voice_guide.mp3",
        },
        "error": None,
    }


def _error_response(code: str, message: str) -> dict:
    return {
        "status": "error",
        "data": None,
        "error": {
            "code": code,
            "message": message,
        },
    }
