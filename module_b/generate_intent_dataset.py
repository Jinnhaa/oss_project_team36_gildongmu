"""
Module B - intent_dataset.csv 자동 생성 코드

역할:
1. 교통 안내 서비스에서 발생할 수 있는 사용자 문장을 시나리오 기반으로 생성한다.
2. 지하철역, 버스정류장, 일반 장소, 교통약자 표현을 포함한다.
3. route_search, last_train_check, alternative_route,
   subway_availability_check, unknown intent 데이터를 만든다.
4. 총 1000개 이상의 학습 데이터셋을 module_b/data/intent_dataset.csv로 저장한다.
"""

import csv
import random
from pathlib import Path


OUTPUT_PATH = Path("module_b/data/intent_dataset.csv")


SUBWAY_STATIONS = [
    "서울역",
    "숙대입구역",
    "홍대입구역",
    "강남역",
    "신촌역",
    "시청역",
    "종로3가역",
    "동대문역",
    "잠실역",
    "사당역",
    "교대역",
    "건대입구역",
    "왕십리역",
    "합정역",
    "여의도역",
    "고속터미널역",
    "을지로입구역",
    "용산역",
    "노량진역",
    "성수역",
]


BUS_STOPS = [
    "서울역버스환승센터",
    "숙대입구역정류장",
    "남영역정류장",
    "홍대입구역정류장",
    "강남역중앙차로",
    "신촌오거리정류장",
    "종로2가정류장",
    "동대문역사문화공원정류장",
    "고속터미널정류장",
    "여의도환승센터",
    "용산역광장정류장",
    "노량진역정류장",
    "합정역정류장",
    "건대입구역정류장",
    "왕십리역정류장",
]


LANDMARKS = [
    "숙명여대정문",
    "서울역광장",
    "남대문시장",
    "서울시청",
    "강남성모병원",
    "세브란스병원",
    "홍대거리",
    "여의도공원",
    "용산전자상가",
    "동대문시장",
    "주민센터",
    "근처 병원",
    "약국",
    "시장",
    "학교",
    "집",
]


LOCATIONS = SUBWAY_STATIONS + BUS_STOPS + LANDMARKS


ROUTE_TEMPLATES = [
    "{start}에서 {end}까지 가고 싶어요",
    "{start}에서 {end}까지 가는 길 알려줘",
    "{start}에서 {end}까지 어떻게 가나요",
    "{start}에서 {end}까지 이동 방법 알려줘",
    "{start}에서 {end}까지 대중교통으로 가고 싶어요",
    "{start} 출발 {end} 도착 경로 알려줘",
    "{start}에서 {end}까지 제일 쉬운 길 알려줘",
    "{start}에서 {end}까지 빠르게 가는 방법 알려줘",
    "{start}에서 {end}까지 안내해줘",
    "{start}에서 {end}까지 길 찾아줘",
    "{end}까지 가야 하는데 {start}에서 어떻게 가요",
    "{start} 근처에서 {end}까지 갈 수 있는 방법 알려줘",
    "{start}에서 출발해서 {end}로 가는 경로 알려줘",
    "{start}에서 {end}까지 환승 적은 경로 알려줘",
    "{start}에서 {end}까지 이동 경로 추천해줘",
    "{start}에서 {end}까지 계단 적은 길로 알려줘",
    "{start}에서 {end}까지 걷기 적은 경로 알려줘",
    "{start}에서 {end}까지 노인이 이동하기 편한 길 알려줘",
    "{start}에서 {end}까지 저상버스 이용 가능한 경로 알려줘",
    "{start}에서 {end}까지 어르신이 가기 쉬운 길 알려줘",
]


LAST_TRAIN_TEMPLATES = [
    "{start}에서 {end}까지 막차 시간이 언제야",
    "{start}에서 {end}까지 가는 막차 알려줘",
    "{start}에서 {end}까지 막차 남았어",
    "{start}에서 {end} 가는 마지막 지하철 알려줘",
    "지금 {start}에서 {end}까지 막차 탈 수 있어",
    "{start} 막차 시간이 궁금해",
    "{end}까지 가는 마지막 차 알려줘",
    "{start}에서 출발하면 {end}까지 막차 가능해",
    "{start}에서 {end}까지 막차 확인해줘",
    "오늘 {start}에서 {end}까지 막차 끝났어",
    "{start}에서 {end} 가는 지하철 마지막 운행 시간 알려줘",
    "지금 출발하면 {end}까지 막차 탈 수 있나요",
    "{start}에서 {end}까지 막차 종료됐는지 알려줘",
    "{start}에서 {end}까지 마지막 열차 시간이 언제야",
    "{end} 방향 막차 아직 남아 있어",
    "{start}에서 {end}까지 버스 막차 남았는지 알려줘",
    "{start}에서 {end}까지 마지막 버스 시간 알려줘",
    "{start}에서 {end}까지 지금 가도 막차 탈 수 있어",
]


ALTERNATIVE_TEMPLATES = [
    "{start}에서 {end}까지 막차 끊겼으면 어떻게 가야 해",
    "{start}에서 {end}까지 지하철이 끝났으면 다른 방법 알려줘",
    "{start}에서 {end}까지 막차 놓쳤을 때 대체 교통수단 알려줘",
    "{start}에서 {end}까지 버스로 갈 수 있는 다른 경로 알려줘",
    "{start}에서 {end}까지 택시 말고 갈 수 있는 방법 있어",
    "{start}에서 {end}까지 지하철이 안 되면 버스 경로 알려줘",
    "{start}에서 {end}까지 대체 경로 추천해줘",
    "{start}에서 {end}까지 다른 교통수단으로 가는 방법 알려줘",
    "{start}에서 {end}까지 막차 끝나면 어떻게 이동해야 해",
    "{start}에서 {end}까지 버스 대체 경로 알려줘",
    "{start}에서 {end}까지 지하철 말고 다른 방법으로 가고 싶어요",
    "{start}에서 {end}까지 밤늦게 갈 수 있는 방법 알려줘",
    "{start}에서 {end}까지 지하철이 없으면 버스나 택시 알려줘",
    "{start}에서 {end}까지 막차 이후 이동 방법 알려줘",
    "{start}에서 {end}까지 다른 방법으로 목적지까지 가고 싶어",
    "{start}에서 {end}까지 교통이 끊겼을 때 갈 수 있는 방법 알려줘",
    "{start}에서 {end}까지 지금 버스라도 탈 수 있어",
    "{start}에서 {end}까지 새벽에 이동할 방법 알려줘",
]


SUBWAY_AVAILABILITY_TEMPLATES = [
    "{start}에서 {end}까지 지금 지하철 탈 수 있어",
    "{start}에서 {end}까지 이 시간에 지하철 운행해",
    "{start}에서 {end}까지 지하철 이용 가능해",
    "{start}에서 {end}까지 아직 지하철 다녀",
    "{start}에서 {end}까지 지하철이 지금 운행 중이야",
    "{start}에서 {end}까지 현재 지하철 이용 가능한지 알려줘",
    "{start}에서 {end}까지 지금 지하철로 이동 가능해",
    "{start}에서 {end}까지 지하철 탈 수 있는 시간인지 확인해줘",
    "{start}에서 {end}까지 지하철 운행 여부 알려줘",
    "{start}에서 {end}까지 지하철 아직 끊기지 않았어",
    "{start}에서 {end}까지 이 시간에도 지하철 가능해",
    "{start}에서 {end}까지 지하철을 이용할 수 있는지 알고 싶어",
    "{start}에서 {end}까지 지하철 운행 중인지 확인해줘",
    "{start}에서 {end}까지 현재 지하철 상태 알려줘",
    "{start}에서 {end}까지 지하철로 갈 수 있는 상황이야",
    "{start}에서 {end}까지 지하철 대신 버스 타야 해",
    "{start}에서 {end}까지 지하철 운행 상태 확인해줘",
    "{start}에서 {end}까지 지금 지하철 이용해도 돼",
]


UNKNOWN_SENTENCES = [
    "오늘 날씨 어때",
    "점심 메뉴 추천해줘",
    "노래 틀어줘",
    "내일 시험 범위 알려줘",
    "버스 기사님 이름 알려줘",
    "휴대폰 배터리 얼마나 남았어",
    "근처 카페 추천해줘",
    "오늘 기분이 안 좋아",
    "숙제가 뭐였지",
    "택배 언제 와",
    "영화 추천해줘",
    "알람 맞춰줘",
    "내 일정 알려줘",
    "뉴스 보여줘",
    "음악 재생해줘",
    "날씨 알려줘",
    "맛집 찾아줘",
    "전화 걸어줘",
    "사진 찍어줘",
    "인터넷 검색해줘",
    "오늘 운세 알려줘",
    "공부 계획 세워줘",
    "영어 단어 외워줘",
    "내 폰 찾아줘",
    "심심해",
    "오늘 뭐 입을까",
    "커피 추천해줘",
    "학교 과제 알려줘",
    "유튜브 틀어줘",
    "일기 써줘",
]


def make_pair_sentences(templates, intent, target_count):
    rows = []
    used_texts = set()

    while len(rows) < target_count:
        start, end = random.sample(LOCATIONS, 2)
        template = random.choice(templates)
        text = template.format(start=start, end=end)

        if text in used_texts:
            continue

        used_texts.add(text)
        rows.append([text, intent])

    return rows


def make_unknown_sentences(target_count):
    rows = []
    used_texts = set()

    prefixes = ["", "혹시 ", "저기 ", "음 ", "지금 ", "오늘 ", "잠깐 "]
    suffixes = ["", " 알려줘", " 궁금해", " 해줄 수 있어", " 부탁해", " 좀 알려줘"]

    while len(rows) < target_count:
        base = random.choice(UNKNOWN_SENTENCES)
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        text = f"{prefix}{base}{suffix}".strip()

        if text in used_texts:
            continue

        used_texts.add(text)
        rows.append([text, "unknown"])

    return rows


def main():
    random.seed(42)

    rows = []
    rows += make_pair_sentences(ROUTE_TEMPLATES, "route_search", 350)
    rows += make_pair_sentences(LAST_TRAIN_TEMPLATES, "last_train_check", 300)
    rows += make_pair_sentences(ALTERNATIVE_TEMPLATES, "alternative_route", 300)
    rows += make_pair_sentences(SUBWAY_AVAILABILITY_TEMPLATES, "subway_availability_check", 300)
    rows += make_unknown_sentences(200)

    random.shuffle(rows)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "intent"])
        writer.writerows(rows)

    print(f"intent_dataset.csv 생성 완료: {OUTPUT_PATH}")
    print(f"총 데이터 수: {len(rows)}")


if __name__ == "__main__":
    main()