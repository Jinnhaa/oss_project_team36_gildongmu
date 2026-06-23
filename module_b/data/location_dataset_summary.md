# location_dataset_v3_all_noisy summary

## 목적
이 데이터셋은 Module B의 장소추출 모델(NER / Slot Filling) 학습용 데이터셋입니다.
모든 장소/역명 표면형을 오인식 또는 비정규 표현으로 구성했습니다.

## 규모
- total: 1600
- train: 1280
- valid: 160
- test: 160

## 라벨
- O
- B-START
- I-START
- B-DEST
- I-DEST

## 컬럼
CSV 컬럼:
`text,start,destination,start_surface,destination_surface,source_type,context_type,split`

JSONL 필드:
`text,tokens,tags,start,destination,start_surface,destination_surface,source_type,context_type,split`

## 설계 기준
- `start`, `destination`: 정답 canonical 역명
- `start_surface`, `destination_surface`: 문장에 실제 등장하는 STT 오인식/비정규 표현
- 모든 row에서 start_surface != start, destination_surface != destination
- `intent` 컬럼 없음: 의도 분류 데이터셋과 혼동 방지
- `context_type`은 문장 맥락 분석용이며 장소추출 학습에서는 사용하지 않아도 됨

## 검증
- tokens/tags 길이 불일치 행: 0
- canonical surface 사용 행: 0

## context_type 분포
{'route_search': 747, 'last_train_check': 384, 'alternative_route': 313, 'subway_availability_check': 156}

## 주요 오인식 표면형 예시 상위 30개
[('서을역', 36), ('사울역', 33), ('서월역', 32), ('서울 여기', 31), ('사울약', 31), ('서울력', 30), ('서울 역', 29), ('서울약', 29), ('서울역이', 29), ('서울 녁', 27), ('서울에', 26), ('서울', 24), ('숙대입구역이', 22), ('숙대 입구역', 22), ('숙대 입고 여기', 20), ('숙대 입국역', 20), ('홍대 입구 여기', 18), ('숙대 입고', 17), ('숙데입구', 17), ('숙대 입구', 17), ('숙대입고', 16), ('숙대입구력', 16), ('숙대입구', 14), ('을지로 이꾸역', 14), ('홍대 입고', 14), ('홍대입국역', 14), ('홍대 입구', 14), ('시청력', 13), ('숙대 입구 여기', 13), ('시청에', 13)]

## 예시

```json
{
  "text": "DMC역 에서 수서약 까지 제일 쉬운 길 알려줘",
  "tokens": [
    "DMC역",
    "에서",
    "수서약",
    "까지",
    "제일",
    "쉬운",
    "길",
    "알려줘"
  ],
  "tags": [
    "B-START",
    "O",
    "B-DEST",
    "O",
    "O",
    "O",
    "O",
    "O"
  ],
  "start": "디지털미디어시티역",
  "destination": "수서역",
  "start_surface": "DMC역",
  "destination_surface": "수서약"
}
```

```json
{
  "text": "왕십리력 에서 가락시장역이 까지 제일 쉬운 길 알려줘",
  "tokens": [
    "왕십리력",
    "에서",
    "가락시장역이",
    "까지",
    "제일",
    "쉬운",
    "길",
    "알려줘"
  ],
  "tags": [
    "B-START",
    "O",
    "B-DEST",
    "O",
    "O",
    "O",
    "O",
    "O"
  ],
  "start": "왕십리역",
  "destination": "가락시장역",
  "start_surface": "왕십리력",
  "destination_surface": "가락시장역이"
}
```

```json
{
  "text": "영등포 역 에서 노량진 역 까지 막차 끊겼나요",
  "tokens": [
    "영등포",
    "역",
    "에서",
    "노량진",
    "역",
    "까지",
    "막차",
    "끊겼나요"
  ],
  "tags": [
    "B-START",
    "I-START",
    "O",
    "B-DEST",
    "I-DEST",
    "O",
    "O",
    "O"
  ],
  "start": "영등포역",
  "destination": "노량진역",
  "start_surface": "영등포 역",
  "destination_surface": "노량진 역"
}
```

```json
{
  "text": "도곡약 까지 가야 하는데 사당약 에서 어떻게 가요",
  "tokens": [
    "도곡약",
    "까지",
    "가야",
    "하는데",
    "사당약",
    "에서",
    "어떻게",
    "가요"
  ],
  "tags": [
    "B-DEST",
    "O",
    "O",
    "O",
    "B-START",
    "O",
    "O",
    "O"
  ],
  "start": "사당역",
  "destination": "도곡역",
  "start_surface": "사당약",
  "destination_surface": "도곡약"
}
```

```json
{
  "text": "뚝섬역이 에서 사당에 까지 어떻게 가나요",
  "tokens": [
    "뚝섬역이",
    "에서",
    "사당에",
    "까지",
    "어떻게",
    "가나요"
  ],
  "tags": [
    "B-START",
    "O",
    "B-DEST",
    "O",
    "O",
    "O"
  ],
  "start": "뚝섬역",
  "destination": "사당역",
  "start_surface": "뚝섬역이",
  "destination_surface": "사당에"
}
```

```json
{
  "text": "사당 여기 에서 서울력 까지 택시 말고 가는 방법 있어",
  "tokens": [
    "사당",
    "여기",
    "에서",
    "서울력",
    "까지",
    "택시",
    "말고",
    "가는",
    "방법",
    "있어"
  ],
  "tags": [
    "B-START",
    "I-START",
    "O",
    "B-DEST",
    "O",
    "O",
    "O",
    "O",
    "O",
    "O"
  ],
  "start": "사당역",
  "destination": "서울역",
  "start_surface": "사당 여기",
  "destination_surface": "서울력"
}
```

```json
{
  "text": "녹사 평 에서 둔촌동역이 까지 제일 쉬운 길 알려줘",
  "tokens": [
    "녹사",
    "평",
    "에서",
    "둔촌동역이",
    "까지",
    "제일",
    "쉬운",
    "길",
    "알려줘"
  ],
  "tags": [
    "B-START",
    "I-START",
    "O",
    "B-DEST",
    "O",
    "O",
    "O",
    "O",
    "O"
  ],
  "start": "녹사평역",
  "destination": "둔촌동역",
  "start_surface": "녹사 평",
  "destination_surface": "둔촌동역이"
}
```

```json
{
  "text": "복정에 에서 문정력 까지 막차 끊겼으면 어떻게 가",
  "tokens": [
    "복정에",
    "에서",
    "문정력",
    "까지",
    "막차",
    "끊겼으면",
    "어떻게",
    "가"
  ],
  "tags": [
    "B-START",
    "O",
    "B-DEST",
    "O",
    "O",
    "O",
    "O",
    "O"
  ],
  "start": "복정역",
  "destination": "문정역",
  "start_surface": "복정에",
  "destination_surface": "문정력"
}
```

```json
{
  "text": "망원역이 에서 사당역이 까지 지하철 운행 중이야",
  "tokens": [
    "망원역이",
    "에서",
    "사당역이",
    "까지",
    "지하철",
    "운행",
    "중이야"
  ],
  "tags": [
    "B-START",
    "O",
    "B-DEST",
    "O",
    "O",
    "O",
    "O"
  ],
  "start": "망원역",
  "destination": "사당역",
  "start_surface": "망원역이",
  "destination_surface": "사당역이"
}
```

```json
{
  "text": "방이에 에서 장지에 까지 막차 끊겼나요",
  "tokens": [
    "방이에",
    "에서",
    "장지에",
    "까지",
    "막차",
    "끊겼나요"
  ],
  "tags": [
    "B-START",
    "O",
    "B-DEST",
    "O",
    "O",
    "O"
  ],
  "start": "방이역",
  "destination": "장지역",
  "start_surface": "방이에",
  "destination_surface": "장지에"
}
```
