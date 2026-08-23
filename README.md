# pair finder — 같은 아이콘 2개 검출기

매칭 게임 화면을 실시간 캡처해서, 서로 같은 아이콘 2개를 빨간 링으로 표시합니다.

## 실행

1. Python 설치
2. `pip install -r requirements.txt`
3. `python find_pair.py` → 전체 화면이 뜨면 게임 보드 영역을 마우스로 드래그하고 ENTER
4. 검출기 창에 빨간 링 2개가 뜨면 게임 창에서 같은 위치를 클릭. `q`로 종료.

## 테스트

```
python find_pair.py --selftest          # video.mp4 기준 회귀 체크
python find_pair.py --video video.mp4   # 녹화 영상으로 동작 확인
```
