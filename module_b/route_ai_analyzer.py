"""
Module B: 장소·의도 분석 및 교통 판단 모듈

역할:
1. Module A에서 전달받은 recognized_text 분석
2. 출발지와 목적지 추출
3. 사용자 의도 분석
4. routes.csv 기반 교통 판단
5. Module C로 전달할 JSON 결과 반환
"""

import csv
from pathlib import Path

try:
    from module_b.predict_bert_intent import predict_intent
except ImportError:
    predict_intent = None

try:
    from module_b.realtime_transport_api import get_realtime_transport_info
except ImportError:
    get_realtime_transport_info = None


def load_station_list(csv_path="module_b/stations.csv"):
    """
    stations.csv 파일에서 역명 사전을 불러온다.
    """

    stations = []
    path = Path(csv_path)

    if not path.exists():
        return stations

    with open(path, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            station_name = row["station_name"].strip()

            if station_name:
                stations.append(station_name)

    return sorted(stations, key=len, reverse=True)


def extract_locations(text):
    """
    사용자 입력 문장에서 출발지와 목적지를 추출한다.

    긴 역명 안에 짧은 역명이 포함되는 경우가 있으므로,
    겹치는 역명은 긴 역명을 우선하고 중복 추출하지 않는다.
    예: 동대문역사문화공원역 안의 동대문역 중복 방지
    """

    found_stations = []

    station_list = load_station_list()

    for station in station_list:
        position = text.find(station)

        if position != -1:
            found_stations.append({
                "station": station,
                "position": position,
                "end_position": position + len(station)
            })

    found_stations.sort(key=lambda item: (item["position"], -len(item["station"])))

    selected_stations = []

    for station_info in found_stations:
        is_overlapped = False

        for selected in selected_stations:
            if (
                station_info["position"] < selected["end_position"] and
                station_info["end_position"] > selected["position"]
            ):
                is_overlapped = True
                break

        if not is_overlapped:
            selected_stations.append(station_info)

    selected_stations.sort(key=lambda item: item["position"])

    if len(selected_stations) >= 2:
        start = selected_stations[0]["station"]
        destination = selected_stations[1]["station"]
        return start, destination

    if len(selected_stations) == 1:
        start = None
        destination = selected_stations[0]["station"]
        return start, destination

    return None, None


def classify_intent(text):
    """
    사용자 입력 문장에서 요청 의도를 분류한다.

    현재 MVP 단계에서는 키워드 기반으로 의도를 분류한다.
    이후 sentence-transformers 기반 의미 유사도 분석으로 확장할 수 있다.
    """

    if "막차" in text or "끊겼" in text or "끊겼나요" in text:
        return "last_train_check"

    if "버스" in text or "대체" in text or "다른 방법" in text:
        return "alternative_route"

    if "지하철" in text and ("가능" in text or "탈 수" in text):
        return "way_availability_check"

    return "route_search"

def classify_intent_with_bert(text, confidence_threshold=0.6):
    """
    BERT 기반 의도 분류를 우선 사용하고,
    모델이 없거나 confidence가 낮은 경우 기존 키워드 기반 classify_intent로 fallback한다.
    """

    if predict_intent is None:
        return {
            "intent": classify_intent(text),
            "confidence": None,
            "method": "keyword_fallback"
        }

    try:
        bert_result = predict_intent(text)
        intent = bert_result["intent"]
        confidence = bert_result["confidence"]

        if confidence < confidence_threshold:
            return {
                "intent": classify_intent(text),
                "confidence": confidence,
                "method": "keyword_fallback_low_confidence"
            }

        return {
            "intent": intent,
            "confidence": confidence,
            "method": "bert"
        }

    except Exception:
        return {
            "intent": classify_intent(text),
            "confidence": None,
            "method": "keyword_fallback_error"
        }


def load_routes(csv_path="module_b/routes.csv"):
    """
    routes.csv 파일을 읽어서 리스트 형태로 반환한다.
    CSV 컬럼명과 값의 앞뒤 공백을 제거하여 KeyError를 방지한다.
    """

    routes = []
    path = Path(csv_path)

    if not path.exists():
        return None

    with open(path, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            clean_row = {}

            for key, value in row.items():
                clean_key = key.strip()
                clean_value = value.strip() if value is not None else value
                clean_row[clean_key] = clean_value

            routes.append(clean_row)

    return routes


def find_route(start, destination, routes):
    """
    출발지와 목적지에 맞는 교통 데이터를 routes.csv에서 찾는다.
    """

    if routes is None:
        return None

    for route in routes:
        if route["start"] == start and route["end"] == destination:
            return route

    return None

def convert_api_result_to_route(api_result, start, destination):
    """
    실시간 교통정보 API 결과를 기존 routes.csv 기반 route 형식과 유사하게 변환한다.

    현재 API 연동 초기 단계에서는 API 응답 구조가 확정되지 않았기 때문에,
    필요한 필드가 없는 경우 기본값을 사용한다.
    """

    data = api_result.get("data", {})

    return {
        "start": start,
        "end": destination,
        "transport": data.get("transport", "subway"),
        "scenario": data.get("scenario", "subway_available"),
        "subway_status": data.get("subway_status", "available"),
        "last_train_status": data.get("last_train_status", "available"),
        "estimated_time": data.get("estimated_time", "실시간 정보 기준"),
        "transfer": data.get("transfer", "실시간 정보 기준")
    }

def make_error(code, message):
    """
    공통 오류 반환 형식
    """

    return {
        "status": "error",
        "data": None,
        "error": {
            "code": code,
            "message": message
        }
    }


def analyze_route(a_result):
    """
    Module A의 결과를 받아 장소·의도 분석 및 교통 판단을 수행한다.

    입력 예시:
    {
        "status": "success",
        "data": {
            "recognized_text": "서울역에서 숙대입구역까지 가고 싶어요"
        },
        "error": None
    }
    """

    if a_result["status"] == "error":
        return a_result

    text = a_result["data"].get("recognized_text")

    if text is None or text.strip() == "":
        return make_error(
            "B_EMPTY_TEXT",
            "분석할 문장이 없습니다."
        )

    start, destination = extract_locations(text)
    intent_result = classify_intent_with_bert(text)
    intent = intent_result["intent"]

    if destination is None:
        return make_error(
            "B_LOCATION_NOT_FOUND",
            "출발지 또는 목적지를 찾을 수 없습니다."
        )

    if start is None:
        return make_error(
            "B_LOCATION_NOT_FOUND",
            "출발지를 찾을 수 없습니다. 출발지를 함께 입력해주세요."
        )

    routes = load_routes()

    route = None
    transport_source = "routes_csv_fallback"

    if get_realtime_transport_info is not None:
        api_result = get_realtime_transport_info(start, destination, intent)

        if api_result.get("status") == "success":
            route = api_result.get("data")
            transport_source = "realtime_api"

    if route is None:
        routes = load_routes()

        if routes is None:
            return make_error(
                "B_DATA_LOAD_FAILED",
                "교통 데이터 파일을 불러오지 못했습니다."
            )

        route = find_route(start, destination, routes)

        if route is None:
            return make_error(
                "B_ROUTE_NOT_FOUND",
                "해당 출발지와 목적지에 맞는 경로 정보를 찾을 수 없습니다."
            )

    result = {
        "status": "success",
        "data": {
            "original_text": text,
            "start": start,
            "destination": destination,
            "intent": intent,
            "scenario": route.get("scenario"),
            "intent_confidence": intent_result.get("confidence"),
            "intent_method": intent_result.get("method"),
            "subway_status": route.get("subway_status"),
            "last_train_status": route.get("last_train_status"),
            "alternative_needed": route.get("transport") != "subway",
            "recommended_transport": route.get("transport"),
            "transport_source": transport_source,
            "route_summary": {
                "start": start,
                "end": destination,
                "transport": route.get("transport"),
                "estimated_time": route.get("estimated_time"),
                "transfer": route.get("transfer"),
                "payment": route.get("payment"),
                "transport_steps": route.get("transport_steps", []),
                "route_steps": route.get("route_steps", [])
            }
        },
        "error": None
    }

    return result


if __name__ == "__main__":
    sample_a_result = {
        "status": "success",
        "data": {
            "recognized_text": "서울역에서 숙대입구역까지 가고 싶어요"
        },
        "error": None
    }

    result = analyze_route(sample_a_result)
    print(result)