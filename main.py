import os
import time  # 시간을 정밀하게 측정하기 위해 추가
import joblib
import numpy as np
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from livekit.api import AccessToken

# 프론트엔드 입력값 검증용 모델
class TokenRequest(BaseModel):
    identity: str = Field(..., description="접속하는 유저의 고유 ID (예: testuser)", min_length=1)
    room_name: str = Field(default="drowsiness-room", description="접속할 실시간 영상 스트리밍 방 이름")
    
# 현재 폴더 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
models = {}

# [변경됨] 유저별로 '처음 눈을 감기 시작한 시간'을 저장할 딕셔너리
user_closed_timestamps = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- 서버가 시작되면서 AI 모델을 불러옵니다... ---")
    try:
        scaler_path = os.path.join(BASE_DIR, "scaler.pkl")
        model_path = os.path.join(BASE_DIR, "drowsiness_model.pkl")

        models["scaler"] = joblib.load(scaler_path)
        models["rf_model"] = joblib.load(model_path)
        print("--- AI 모델 로드 완료! ---")
    except FileNotFoundError as e:
        print(f"❌ 파일 에러: {e}")

    yield
    models.clear()
    print("--- 서버가 종료되었습니다. ---")


app = FastAPI(lifespan=lifespan)
# 기존에 있던 app = FastAPI(...) 코드 바로 아랫줄에 붙여넣으세요!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# [핵심] 5초 이상 눈 감김 지속 여부 판단 로직
def predict_drowsiness(user_id, ear, mar, head_angle):
    scaler = models["scaler"]
    rf_model = models["rf_model"]

    # 1. 기존 모델 구조가 필요로 하는 Feature들을 넣어 예측 수행 (0, 1, 2, 3 중 반환)
    input_data = np.array([[ear, mar, head_angle]])
    scaled_data = scaler.transform(input_data)
    raw_prediction = rf_model.predict(scaled_data)[0]


    current_time = time.time()  # 현재 시간 측정 (초 단위)

    # 2. 모델 예측 결과가 2(눈감김)인 경우
    if raw_prediction == 2:
        # 이 유저가 방금 막 처음으로 눈을 감았다면, 그 시점의 시간을 기록
        if user_id not in user_closed_timestamps or user_closed_timestamps[user_id] is None:
            user_closed_timestamps[user_id] = current_time
            print(f"[{user_id}] 눈 감김 시작 감지. 타이머 시작!")

        # 눈을 감고 있은 지 얼마나 지났는지 계산 (현재 시간 - 처음 감은 시간)
        elapsed_time = current_time - user_closed_timestamps[user_id]
        print(f"[{user_id}] 눈 감김 지속 시간: {elapsed_time:.2f}초")

        # 5.0초 이상 지속되었다면 최종 졸음(DROWSY)으로 판단
        if elapsed_time >= 5.0:
            return "DROWSY"
        else:
            return "FOCUS"  # 5초가 되기 전까지는 일반 깜빡임이나 대기 상태이므로 정상 처리

    # 3. 눈을 떴거나(0), 제외하기로 한 하품(2)/고개숙임(3)이 나온 경우
    else:
        # 눈을 뜬 것으로 간주하여 타이머를 초기화(리셋)합니다.
        user_closed_timestamps[user_id] = None
        return "FOCUS"


@app.get("/")
def read_root():
    return {"message": "AI 졸음 감지 서버가 정상 작동 중입니다."}


@app.websocket("/ws/drowsiness/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    print(f"접속 성공: 유저 {user_id}님이 연결되었습니다.")

    try:
        while True:
            data = await websocket.receive_json()

            ear = float(data.get('ear', 0))
            mar = float(data.get('mar', 0))
            head_angle = float(data.get('head_angle', 0))

            # AI 및 5초 타이머 로직 실행
            status = predict_drowsiness(user_id, ear, mar, head_angle)

            # 결과를 다시 프론트로 전송
            await websocket.send_json({"status": status})

    except WebSocketDisconnect:
        print(f"접속 종료: 유저 {user_id}님이 나갔습니다.")
        # 메모리 관리를 위해 유저가 나가면 타이머 데이터 삭제
        if user_id in user_closed_timestamps:
            del user_closed_timestamps[user_id]
            # 보안용 환경변수 설정 (기본값 세팅)
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")

@app.post("/api/livekit/token", summary="LiveKit 스트리밍 토큰 자동 발급", tags=["Streaming"])
def generate_livekit_token(request: TokenRequest):
    """
    프론트엔드 요청 시 라이브키트 방 진입용 토큰을 자동으로 생성합니다.
    """
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="서버 설정 오류: LiveKit Key가 없습니다.")
        
    try:
        grant = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(request.identity) \
            .with_name(request.identity)
            
        grant.with_grants(AccessToken.Grants(
            room_join=True,
            room=request.room_name,
            can_publish=True,
            can_subscribe=True
        ))

        token_jwt = grant.to_jwt()

        return {
            "success": True,
            "token": token_jwt,
            "room_name": request.room_name,
            "identity": request.identity
        }

    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"토큰 생성 실패: {str(e)}")
