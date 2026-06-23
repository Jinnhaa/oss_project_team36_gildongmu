"""
Module B - 장소 추출 NER 모델 테스트 코드

실행:
python3 module_b/test_location_ner.py
"""

from module_b.predict_location_ner import predict_locations


TESTS = [
    ("사울약에서 숙대입고까지 가고 싶어", "서울역", "숙대입구역"),
    ("서울약 에서 숙대 입고 여기 까지 가고 싶어요", "서울역", "숙대입구역"),
    ("서울력에서 숙대 입구 여기까지 막차 남았어", "서울역", "숙대입구역"),
    ("강남약에서 숙대입고까지 막차 남았어?", "강남역", "숙대입구역"),
    ("홍대 입구 약에서 사울역까지 가는 길 알려줘", "홍대입구역", "서울역"),
]


def main():
    passed = 0

    for text, expected_start, expected_destination in TESTS:
        result = predict_locations(text)

        print("입력:", text)
        print("예측:", result)

        ok = (
            result is not None
            and result.get("start") == expected_start
            and result.get("destination") == expected_destination
        )

        if ok:
            print("결과: 성공")
            passed += 1
        else:
            print("결과: 실패")
            print("예상:", expected_start, expected_destination)

        print("-" * 60)

    print(f"전체 {len(TESTS)}개 중 {passed}개 성공")


if __name__ == "__main__":
    main()
