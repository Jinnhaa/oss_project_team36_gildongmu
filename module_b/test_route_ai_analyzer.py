"""
Module B 테스트 실행 파일

역할:
1. test_cases.csv 파일을 읽는다.
2. 각 테스트 문장을 analyze_route()에 넣는다.
3. 예상 출발지, 목적지, 의도와 실제 결과를 비교한다.
4. 테스트 성공/실패 결과를 출력한다.

실행 방법:
python3 module_b/test_route_ai_analyzer.py
"""

import csv
from route_ai_analyzer import analyze_route


def load_test_cases(csv_path="module_b/test_cases.csv"):
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


def make_sample_a_result(input_text):
    return {
        "status": "success",
        "data": {
            "recognized_text": input_text
        },
        "error": None
    }


def run_tests():
    test_cases = load_test_cases()

    total_count = len(test_cases)
    pass_count = 0
    fail_count = 0

    print("Module B 테스트를 시작합니다.")
    print("-" * 50)

    for index, case in enumerate(test_cases, start=1):
        input_text = case["input_text"]
        expected_start = case["expected_start"]
        expected_destination = case["expected_destination"]
        expected_intent = case["expected_intent"]

        sample_a_result = make_sample_a_result(input_text)
        result = analyze_route(sample_a_result)

        print(f"[Test {index}] 입력 문장: {input_text}")

        if result["status"] == "error":
            print("결과: 실패")
            print(f"오류 코드: {result['error']['code']}")
            print(f"오류 메시지: {result['error']['message']}")
            fail_count += 1
            print("-" * 50)
            continue

        data = result["data"]

        actual_start = data["start"]
        actual_destination = data["destination"]
        actual_intent = data["intent"]

        is_passed = (
            actual_start == expected_start and
            actual_destination == expected_destination and
            actual_intent == expected_intent
        )

        if is_passed:
            print("결과: 성공")
            pass_count += 1
        else:
            print("결과: 실패")
            fail_count += 1
            print(f"예상 start: {expected_start} / 실제 start: {actual_start}")
            print(f"예상 destination: {expected_destination} / 실제 destination: {actual_destination}")
            print(f"예상 intent: {expected_intent} / 실제 intent: {actual_intent}")

        print("-" * 50)

    print("테스트 완료")
    print(f"전체 테스트 수: {total_count}")
    print(f"성공: {pass_count}")
    print(f"실패: {fail_count}")


if __name__ == "__main__":
    run_tests()