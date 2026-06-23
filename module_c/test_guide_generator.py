"""
Module C 테스트 실행 파일

역할:
1. test_cases.csv 파일을 읽는다.
2. 각 테스트 케이스를 generate_guide()에 넣는다.
3. 정상 결과와 의도된 오류 결과를 모두 테스트한다.

실행 방법:
py module_c/test_guide_generator.py
"""

import csv
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from module_c.guide_generator import generate_guide


def load_test_cases(csv_path="module_c/test_cases.csv"):
    test_cases = []

    with open(csv_path, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            clean_row = {}

            for key, value in row.items():
                clean_key = key.strip()
                clean_value = value.strip() if value is not None else value
                clean_row[clean_key] = clean_value

            test_cases.append(clean_row)

    return test_cases


def make_b_result(case):
    if case["scenario"] == "b_error":
        return {
            "status": "error",
            "data": None,
            "error": {"code": "B_ROUTE_NOT_FOUND", "message": "경로를 찾을 수 없습니다."},
        }

    return {
        "status": "success",
        "data": {
            "start": case["start"],
            "destination": case["destination"],
            "intent": "route_search",
            "scenario": case["scenario"],
            "recommended_transport": "subway",
            "route_summary": {
                "estimated_time": case["estimated_time"],
                "transfer": case["transfer"],
            },
        },
        "error": None,
    }


def run_tests():
    test_cases = load_test_cases()

    total_count = len(test_cases)
    pass_count = 0
    fail_count = 0

    print("Module C 테스트를 시작합니다.")
    print("-" * 50)

    for index, case in enumerate(test_cases, start=1):
        expected_status     = case["expected_status"]
        expected_screen_type = case["expected_screen_type"]
        expected_error_code = case["expected_error_code"]

        b_result = make_b_result(case)
        result   = generate_guide(b_result)

        print(f"[Test {index}] 시나리오: {case['scenario']}")

        if expected_status == "error":
            if result["status"] == "error" and result["error"]["code"] == expected_error_code:
                print("결과: 성공")
                print(f"의도된 오류 처리 확인: {expected_error_code}")
                pass_count += 1
            else:
                print("결과: 실패")
                print(f"예상 오류 코드: {expected_error_code}")
                print(f"실제 결과: {result}")
                fail_count += 1

            print("-" * 50)
            continue

        if result["status"] == "error":
            print("결과: 실패")
            print(f"오류 코드: {result['error']['code']}")
            print(f"오류 메시지: {result['error']['message']}")
            fail_count += 1
            print("-" * 50)
            continue

        actual_screen_type = result["data"]["screen_type"]

        if actual_screen_type == expected_screen_type:
            print("결과: 성공")
            print(f"screen_type: {actual_screen_type}")
            print(f"title: {result['data']['title']}")
            pass_count += 1
        else:
            print("결과: 실패")
            print(f"예상 screen_type: {expected_screen_type} / 실제: {actual_screen_type}")
            fail_count += 1

        print("-" * 50)

    print("테스트 완료")
    print(f"전체 테스트 수: {total_count}")
    print(f"성공: {pass_count}")
    print(f"실패: {fail_count}")


if __name__ == "__main__":
    run_tests()
