# pair finder — 같은 아이콘 2개 검출기

매칭 게임 화면을 실시간 캡처해서, 서로 같은 아이콘 2개를 빨간 링으로 표시합니다.

## 실행

1. Python 설치
2. `pip install -r requirements.txt`
3. `python find_pair.py` → 전체 화면이 뜨면 게임 보드 영역을 마우스로 드래그하고 ENTER.
   선택한 영역이 `선택한 영역: --roi x,y,w,h` 로 출력됩니다.
4. 검출기 창에 빨간 링 2개가 뜨면 게임 창에서 같은 위치를 클릭. `q`로 종료.

## 옵션

| 옵션 | 설명 |
|---|---|
| `--roi x,y,w,h` | 게임 영역을 직접 지정해 드래그 선택을 생략. 3단계에서 출력된 값을 그대로 쓰면 됩니다. |
| `--threshold 0.8` | 같은 아이콘으로 볼 최소 유사도 (기본 0.8). 낮추면 더 잘 잡지만 오검출이 늘어납니다. |
| `--video 파일` | 화면 대신 녹화 영상을 입력으로 사용 |
| `--selftest` | `video.mp4` 기준 회귀 체크 |

```
python find_pair.py --roi 100,200,558,700 --threshold 0.75
```

## 테스트

```
python find_pair.py --selftest          # video.mp4 기준 회귀 체크
python find_pair.py --video video.mp4   # 녹화 영상으로 동작 확인
```

`video.mp4` 는 저장소에 포함되어 있지 않습니다. 정답 좌표(`SELFTEST_EXPECTED`)는 원본 녹화 영상
(폭 558 px) 기준이라, 영상이 없으면 `--selftest` 는 `영상을 열 수 없음: video.mp4` 를 출력하고 종료합니다.
