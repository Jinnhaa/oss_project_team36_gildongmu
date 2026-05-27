"""
Module B - ODsay 대중교통 길찾기 API 단독 테스트

실행 전:
터미널에서 ODSAY_API_KEY 환경변수를 설정해야 한다.

예:
export ODSAY_API_KEY="발급받은_ODsay_API_Key"

실행:
python3 module_b/test_realtime_transport_api.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from module_b.realtime_transport_api import get_realtime_transport_info


def run_test():
    start = "서울역"
    destination = "숙대입구역"
    intent = "route_search"

    result = get_realtime_transport_info(start, destination, intent)

    print("ODsay API 테스트 결과")
    print("-" * 40)
    print("출발지:", start)
    print("도착지:", destination)
    print("의도:", intent)
    print("-" * 40)
    print(result)

    if result["status"] == "success":
        print("\n결과: 성공")
        print("예상 소요 시간:", result["data"].get("estimated_time"))
        print("환승 정보:", result["data"].get("transfer"))
        print("교통수단:", result["data"].get("transport"))
        print("요금:", result["data"].get("payment"))
    else:
        print("\n결과: 실패")
        print("오류 코드:", result["error"].get("code"))
        print("오류 메시지:", result["error"].get("message"))


if __name__ == "__main__":
    run_test()