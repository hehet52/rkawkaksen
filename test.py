import cv2
import mediapipe as mp
import numpy as np
import pickle
from scipy.spatial import distance

# ── 모델 & 스케일러 불러오기 ───────────────────────────
with open("drowsiness_model.pkl", "rb") as f:
    model = pickle.load(f)
with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

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

label_map  = {0:"정상", 1:"눈감김", 2:"하품", 3:"고개숙임"}
color_map  = {0:(0,200,0), 1:(0,0,255), 2:(0,165,255), 3:(255,0,0)}

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
    nose = np.array([lm[1].x * w, lm[1].y * h])
    chin = np.array([lm[152].x * w, lm[152].y * h])
    return np.degrees(np.arctan2(chin[1]-nose[1], chin[0]-nose[0]))

# ══════════════════════════════════════════════════════
# ↓↓↓ 테스트할 영상 파일 경로를 여기에 입력하세요 ↓↓↓
VIDEO_PATH = "videoes/normal/정상1.mp4"
# ══════════════════════════════════════════════════════

cap = cv2.VideoCapture(VIDEO_PATH)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    if result.multi_face_landmarks:
        lm = result.multi_face_landmarks[0].landmark

        ear   = (calc_ear(lm, LEFT_EYE, w, h) + calc_ear(lm, RIGHT_EYE, w, h)) / 2.0
        mar   = calc_mar(lm, w, h)
        angle = calc_head_angle(lm, w, h)

        # 모델 예측
        features = scaler.transform([[ear, mar, angle]])
        pred     = model.predict(features)[0]
        label    = label_map[pred]
        color    = color_map[pred]

        # 화면 출력
        cv2.putText(frame, f"상태: {label}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        cv2.putText(frame, f"EAR:{ear:.2f} MAR:{mar:.2f} Angle:{angle:.1f}",
                    (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

    cv2.imshow("Drowsiness Test", frame)

    # Q 누르면 종료, 스페이스바로 일시정지
    key = cv2.waitKey(30) & 0xFF
    if key == ord('q'):
        break
    elif key == ord(' '):
        cv2.waitKey(0)

cap.release()
cv2.destroyAllWindows()