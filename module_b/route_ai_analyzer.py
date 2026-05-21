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


STATION_LIST = [
    "서울역",
    "숙대입구역",
    "을지로입구역",
    "시청역",
    "명동역",
    "용산역",
    "공덕역",
    "홍대입구역",
    "동대문역사문화공원역",
    "강남역"
]


def extract_locations(text):
    """
    사용자 입력 문장에서 출발지와 목적지를 추출한다.

    현재 MVP 단계에서는 STATION_LIST에 등록된 역명이
    문장에 등장한 순서대로 출발지와 목적지를 판단한다.
    """

    found_stations = []

    for station in STATION_LIST:
        position = text.find(station)

        if position != -1:
            found_stations.append({
                "station": station,
                "position": position
            })

    found_stations.sort(key=lambda item: item["position"])

    if len(found_stations) >= 2:
        start = found_stations[0]["station"]
        destination = found_stations[1]["station"]
        return start, destination

    if len(found_stations) == 1:
        start = None
        destination = found_stations[0]["station"]
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
        return "subway_availability_check"

    return "route_search"


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
    intent = classify_intent(text)

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
            "scenario": route["scenario"],
            "subway_status": route["subway_status"],
            "last_train_status": route["last_train_status"],
            "alternative_needed": route["transport"] != "subway",
            "recommended_transport": route["transport"],
            "route_summary": {
                "start": route["start"],
                "end": route["end"],
                "transport": route["transport"],
                "estimated_time": route["estimated_time"],
                "transfer": route["transfer"]
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