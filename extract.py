import cv2
import mediapipe as mp
import numpy as np
import csv
import os
import glob
from scipy.spatial import distance

# ── MediaPipe 초기화 ───────────────────────────────────
mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ── 랜드마크 인덱스 ────────────────────────────────────
LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]
MOUTH     = [61, 291, 39, 181, 0, 17, 269, 405]

# ── 특징값 계산 함수들 ─────────────────────────────────
def calc_ear(lm, indices, w, h):
    pts = [(lm[i].x * w, lm[i].y * h) for i in indices]
    A = distance.euclidean(pts[1], pts[5])
    B = distance.euclidean(pts[2], pts[4])
    C = distance.euclidean(pts[0], pts[3])
    return (A + B) / (2.0 * C)

def calc_mar(lm, w, h):
    pts = [(lm[i].x * w, lm[i].y * h) for i in MOUTH]
    A = distance.euclidean(pts[2], pts[6])
    B = distance.euclidean(pts[3], pts[5])
    C = distance.euclidean(pts[0], pts[1])
    return (A + B) / (2.0 * C)

def calc_head_angle(lm, w, h):
    nose = np.array([lm[1].x * w,   lm[1].y * h])
    chin = np.array([lm[152].x * w, lm[152].y * h])
    dy = chin[1] - nose[1]
    dx = chin[0] - nose[0]
    return np.degrees(np.arctan2(dy, dx))

# ── 영상 1개 → CSV 행 추출 ─────────────────────────────
def extract_from_video(video_path, label):
    cap = cv2.VideoCapture(video_path)
    rows = []
    frame_idx = 0

    print(f"  처리 중: {os.path.basename(video_path)}")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb)

        if result.multi_face_landmarks:
            lm = result.multi_face_landmarks[0].landmark
            ear   = (calc_ear(lm, LEFT_EYE, w, h) + calc_ear(lm, RIGHT_EYE, w, h)) / 2.0
            mar   = calc_mar(lm, w, h)
            angle = calc_head_angle(lm, w, h)
            rows.append([round(ear, 4), round(mar, 4), round(angle, 4), label])

        frame_idx += 1

    cap.release()
    print(f"  → {len(rows)}개 프레임 추출 완료")
    return rows

# ══════════════════════════════════════════════════════
#  메인: 폴더별로 영상 전체 처리
# ══════════════════════════════════════════════════════

# 상태별 폴더 이름과 라벨 번호
# 라벨: 0=정상, 1=눈감김, 2=하품, 3=고개숙임
CATEGORIES = {
    "normal":     0,
    "eye_closed": 1,
    "yawn":       2,
    "head_down":  3,
}

os.makedirs("csv", exist_ok=True)

for folder, label in CATEGORIES.items():
    video_folder = os.path.join("videoes", folder)
    # mp4, avi, mov 형식 모두 지원
    video_files = (
        glob.glob(os.path.join(video_folder, "*.mp4")) +
        glob.glob(os.path.join(video_folder, "*.avi")) +
        glob.glob(os.path.join(video_folder, "*.mov"))
    )

    if not video_files:
        print(f"⚠ videoes/{folder}/ 에 영상이 없습니다. 건너뜀.")
        continue

    all_rows = []
    print(f"\n[{folder}] 영상 {len(video_files)}개 처리 시작")

    for vf in video_files:
        all_rows.extend(extract_from_video(vf, label))

    # 상태별 CSV 저장
    out_path = os.path.join("csv", f"{folder}.csv")
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["EAR", "MAR", "HeadAngle", "Label"])
        writer.writerows(all_rows)

    print(f"✅ 저장 완료: {out_path} (총 {len(all_rows)}행)")

print("\n🎉 모든 영상 처리 완료!")