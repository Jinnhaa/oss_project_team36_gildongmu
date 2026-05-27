"""
Module B - 실시간 교통정보 API 연동 모듈

역할:
1. 실시간 교통정보 API 조회를 담당한다.
2. API 키가 없거나 API 호출이 실패하면 error 결과를 반환한다.
3. route_ai_analyzer.py에서는 API 실패 시 routes.csv를 fallback으로 사용한다.

주의:
현재 기본 구현은 API 연동 구조를 반영하기 위한 안전한 wrapper이다.
실제 API 키와 endpoint가 준비되면 get_realtime_transport_info() 내부를 확장한다.
"""

import os
import requests


def make_api_error(code, message):
    return {
        "status": "error",
        "data": None,
        "error": {
            "code": code,
            "message": message
        }
    }


def get_realtime_transport_info(start, destination, intent=None):
    """
    출발지와 목적지를 기반으로 실시간 교통정보 API를 조회한다.

    현재 버전:
    - 환경변수 SEOUL_TRANSPORT_API_KEY가 없으면 API 조회를 수행하지 않는다.
    - 이 경우 route_ai_analyzer.py에서 routes.csv fallback을 사용한다.

    추후 확장:
    - 서울시 지하철 실시간 도착정보 API
    - 서울시 버스 도착정보 API
    - 공공데이터포털 TAGO API 등과 연결 가능
    """

    api_key = os.getenv("SEOUL_TRANSPORT_API_KEY")

    if not api_key:
        return make_api_error(
            "API_KEY_MISSING",
            "실시간 교통정보 API 키가 설정되어 있지 않습니다."
        )

    try:
        # 실제 API endpoint가 확정되면 이 부분을 수정한다.
        # 지금은 구조만 유지하기 위해 예시 URL을 둔다.
        endpoint = "https://example.com/realtime-transport"

        params = {
            "serviceKey": api_key,
            "start": start,
            "destination": destination,
            "intent": intent
        }

        response = requests.get(endpoint, params=params, timeout=5)
        response.raise_for_status()

        api_data = response.json()

        return {
            "status": "success",
            "data": api_data,
            "error": None
        }

    except Exception as error:
        return make_api_error(
            "API_REQUEST_FAILED",
            f"실시간 교통정보 API 조회에 실패했습니다: {str(error)}"
        )