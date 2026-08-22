"""매칭 게임 보드에서 서로 같은 아이콘 2개를 찾아 빨간 링으로 표시.

사용법:
  python find_pair.py                # 실시간 화면 감시 (시작 시 게임 영역 드래그 지정)
  python find_pair.py --video v.mp4  # 녹화 영상으로 테스트
  python find_pair.py --selftest     # video.mp4 기준 회귀 체크
"""
import argparse
import itertools
import sys

import cv2
import numpy as np

BASE_W = 558  # 파라미터 튜닝 기준 해상도(video.mp4 폭). ROI 폭에 비례해 스케일.
MIN_SIM = 0.8


def find_pair(img):
    """보드가 보이면 ((x1,y1),(x2,y2)), 유사도 반환. 아니면 None."""
    scale = img.shape[1] / BASE_W
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=int(60 * scale),
        param1=100, param2=30,
        minRadius=int(25 * scale), maxRadius=int(45 * scale))
    if circles is None:
        return None
    big_r, small_r = int(36 * scale), int(28 * scale)
    crops = []
    for x, y, r in np.round(circles[0]).astype(int):
        big = img[y - big_r:y + big_r, x - big_r:x + big_r]
        small = img[y - small_r:y + small_r, x - small_r:x + small_r]
        if big.shape[:2] == (2 * big_r, 2 * big_r) and \
           small.shape[:2] == (2 * small_r, 2 * small_r):
            crops.append(((x, y), big, small))
    if len(crops) < 20:  # 보드 전환 애니메이션 중이면 표시하지 않음
        return None
    best, pair = -1.0, None
    for (p1, b1, s1), (p2, b2, s2) in itertools.combinations(crops, 2):
        # 작은 크롭을 큰 크롭 위에서 슬라이딩 → 원 중심 오차에 강함
        sim = max(cv2.matchTemplate(b1, s2, cv2.TM_CCOEFF_NORMED).max(),
                  cv2.matchTemplate(b2, s1, cv2.TM_CCOEFF_NORMED).max())
        if sim > best:
            best, pair = sim, (p1, p2)
    if best < MIN_SIM:
        return None
    return pair, best


def frames_from_video(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        sys.exit(f"영상을 열 수 없음: {path}")
    while True:
        ok, frame = cap.read()
        if not ok:
            return
        yield frame


def frames_from_screen():
    import mss
    with mss.mss() as sct:
        mon = sct.monitors[1]
        full = np.ascontiguousarray(np.array(sct.grab(mon))[:, :, :3])
        title = "게임 영역을 드래그 후 ENTER"
        x, y, w, h = cv2.selectROI(title, full, showCrosshair=False)
        cv2.destroyWindow(title)
        if not w or not h:
            sys.exit("영역이 지정되지 않았습니다.")
        box = {"left": mon["left"] + x, "top": mon["top"] + y,
               "width": w, "height": h}
        while True:
            yield np.ascontiguousarray(np.array(sct.grab(box))[:, :, :3])


def watch(frames, delay_ms):
    win = "pair finder (q: 종료)"
    prev_small, result = None, None
    for img in frames:
        if img.shape[1] != BASE_W:  # 고해상도 캡처여도 연산 비용을 기준 해상도로 고정
            img = cv2.resize(img, (BASE_W, img.shape[0] * BASE_W // img.shape[1]))
        # 화면이 바뀐 프레임에서만 검출 실행 (보드는 클릭 전까지 정지 화면)
        small = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (64, 64))
        if prev_small is None or cv2.absdiff(small, prev_small).mean() > 2:
            result = find_pair(img)
        prev_small = small
        view = img.copy()
        if result:
            (p1, p2), sim = result
            ring_r = int(44 * img.shape[1] / BASE_W)
            for p in (p1, p2):
                cv2.circle(view, p, ring_r, (0, 0, 255), 4)
        cv2.imshow(win, view)
        if cv2.waitKey(delay_ms) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()


# 수동 확인한 정답 쌍: 프레임 번호 -> 같은 아이콘 2개의 중심 좌표
SELFTEST_EXPECTED = {
    15: ((218, 193), (217, 529)),    # 개 아이콘 쌍
    200: ((329, 77), (329, 191)),    # 태양 아이콘 쌍
    500: ((442, 77), (217, 419)),    # EVM 아이콘 쌍
}


def selftest(video):
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        sys.exit(f"영상을 열 수 없음: {video}")

    def close(a, b):
        return abs(a[0] - b[0]) < 15 and abs(a[1] - b[1]) < 15

    for idx, want in SELFTEST_EXPECTED.items():
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, img = cap.read()
        assert ok, f"frame {idx}: 읽기 실패"
        result = find_pair(img)
        assert result, f"frame {idx}: 쌍을 찾지 못함"
        got, sim = result
        assert (close(got[0], want[0]) and close(got[1], want[1])) or \
               (close(got[0], want[1]) and close(got[1], want[0])), \
               f"frame {idx}: got {got}, want {want}"
        print(f"frame {idx}: OK pair={got} sim={sim:.3f}")
    print("selftest passed")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", help="화면 대신 영상 파일을 입력으로 사용")
    ap.add_argument("--selftest", action="store_true",
                    help="video.mp4로 검출 로직 회귀 체크")
    args = ap.parse_args()
    if args.selftest:
        selftest(args.video or "video.mp4")
    elif args.video:
        watch(frames_from_video(args.video), delay_ms=33)
    else:
        watch(frames_from_screen(), delay_ms=30)  # 평시 틱 비용 ~0.3ms라 30ms로 촘촘히


if __name__ == "__main__":
    main()
