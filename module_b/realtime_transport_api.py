"""
Module B - ODsay 대중교통 길찾기 API 연동 모듈

역할:
1. stations.csv에서 출발지/도착지 좌표를 찾는다.
2. ODsay 대중교통 길찾기 API를 호출한다.
3. API 결과를 route_ai_analyzer.py에서 사용할 수 있는 형식으로 변환한다.
4. API 키 누락, 좌표 누락, 호출 실패 시 error를 반환하여 routes.csv fallback이 가능하게 한다.
"""

import csv
import os
from pathlib import Path

import requests


STATIONS_PATH = Path("module_b/stations.csv")
ODSAY_API_URL = "https://api.odsay.com/v1/api/searchPubTransPathT"


def make_api_error(code, message):
    return {
        "status": "error",
        "data": None,
        "error": {
            "code": code,
            "message": message,
        },
    }


def load_station_coordinates():
    """
    stations.csv에서 station_name, lat, lng 정보를 읽는다.
    lat/lng가 비어 있는 역은 좌표 조회 대상에서 제외한다.
    """

    if not STATIONS_PATH.exists():
        return {}

    station_map = {}

    with open(STATIONS_PATH, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            station_name = (row.get("station_name") or "").strip()
            lat = (row.get("lat") or "").strip()
            lng = (row.get("lng") or "").strip()

            if not station_name or not lat or not lng:
                continue

            try:
                station_map[station_name] = {
                    "lat": float(lat),
                    "lng": float(lng),
                }
            except ValueError:
                continue

    return station_map


def get_station_coordinate(station_name):
    station_map = load_station_coordinates()
    return station_map.get(station_name)


def summarize_odsay_path(api_json):
    """
    ODsay 응답에서 첫 번째 추천 경로를 요약한다.
    """

    result = api_json.get("result", {})
    paths = result.get("path", [])

    if not paths:
        return None

    first_path = paths[0]
    info = first_path.get("info", {})

    total_time = info.get("totalTime")
    payment = info.get("payment")
    bus_transit_count = info.get("busTransitCount", 0)
    subway_transit_count = info.get("subwayTransitCount", 0)
    total_station_count = info.get("totalStationCount")
    first_start_station = info.get("firstStartStation", "")
    last_end_station = info.get("lastEndStation", "")

    sub_paths = first_path.get("subPath", [])
    transport_steps = []

    for sub_path in sub_paths:
        traffic_type = sub_path.get("trafficType")

        if traffic_type == 1:
            transport_steps.append("지하철")
        elif traffic_type == 2:
            transport_steps.append("버스")
        elif traffic_type == 3:
            transport_steps.append("도보")

    unique_steps = []
    for step in transport_steps:
        if not unique_steps or unique_steps[-1] != step:
            unique_steps.append(step)

    if "지하철" in unique_steps and "버스" in unique_steps:
        transport = "subway+bus"
    elif "지하철" in unique_steps:
        transport = "subway"
    elif "버스" in unique_steps:
        transport = "bus"
    else:
        transport = "walk"

    transfer_count = bus_transit_count + subway_transit_count

    return {
        "transport": transport,
        "scenario": "realtime_route_found",
        "subway_status": "available" if "지하철" in unique_steps else "not_used",
        "last_train_status": "unknown",
        "estimated_time": f"약 {total_time}분" if total_time is not None else "확인 불가",
        "transfer": f"{transfer_count}회 환승" if transfer_count else "환승 없음",
        "payment": payment,
        "total_station_count": total_station_count,
        "first_start_station": first_start_station,
        "last_end_station": last_end_station,
        "transport_steps": unique_steps,
    }


def get_realtime_transport_info(start, destination, intent=None):
    """
    출발지와 목적지를 기반으로 ODsay 대중교통 길찾기 API를 호출한다.
    """

    api_key = os.getenv("ODSAY_API_KEY")

    if not api_key:
        return make_api_error(
            "API_KEY_MISSING",
            "ODSAY_API_KEY 환경변수가 설정되어 있지 않습니다.",
        )

    start_coord = get_station_coordinate(start)
    destination_coord = get_station_coordinate(destination)

    if start_coord is None:
        return make_api_error(
            "API_START_COORD_NOT_FOUND",
            f"출발지 좌표를 찾을 수 없습니다: {start}",
        )

    if destination_coord is None:
        return make_api_error(
            "API_DESTINATION_COORD_NOT_FOUND",
            f"도착지 좌표를 찾을 수 없습니다: {destination}",
        )

    params = {
        "SX": start_coord["lng"],
        "SY": start_coord["lat"],
        "EX": destination_coord["lng"],
        "EY": destination_coord["lat"],
        "apiKey": api_key,
    }

    try:
        response = requests.get(ODSAY_API_URL, params=params, timeout=10)
        response.raise_for_status()
        api_json = response.json()

        if "error" in api_json:
            error = api_json["error"]
            return make_api_error(
                "ODSAY_API_ERROR",
                f"ODsay API 오류: {error}",
            )

        summary = summarize_odsay_path(api_json)

        if summary is None:
            return make_api_error(
                "ODSAY_ROUTE_NOT_FOUND",
                "ODsay API에서 대중교통 경로를 찾지 못했습니다.",
            )

        return {
            "status": "success",
            "data": summary,
            "error": None,
        }

    except Exception as error:
        return make_api_error(
            "API_REQUEST_FAILED",
            f"ODsay 대중교통 길찾기 API 조회 실패: {str(error)}",
        )