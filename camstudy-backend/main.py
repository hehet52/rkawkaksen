import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from livekit import api  # 최신 라이브키트 api 패키지 사용

app = FastAPI()

# 브라우저에서 차단당하지 않도록 CORS 설정을 열어줍니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 파일들이 위치한 현재 폴더 경로를 계산합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. 룸 입장 화면 (HTML 페이지 쏴주기)
@app.get("/room")
def read_room_page():
    html_path = os.path.join(current_dir, "index.html")
    if not os.path.exists(html_path):
        return {"error": "index.html 파일을 찾을 수 없습니다. 경로를 확인해 주세요."}
    return FileResponse(html_path)

# 2. LiveKit 토큰 발급 API (최신 livekit-api 규격 반영)
@app.get("/api/get-token")
def get_token(room_name: str, user_name: str):
    # 본인의 발급받은 키 정보를 여기에 정확히 넣으세요!
    LIVEKIT_API_KEY = "devkey"
    LIVEKIT_API_SECRET = "secret"

    try:
        # 최신 livekit 라이브러리는 가드(Grants)를 아래 방식으로 선언해야 에러가 안 납니다.
        token = (
            api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
            .with_identity(user_name)
            .with_name(user_name)
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                )
            )
        )
        
        # 주주의 최신 라이브러리 문법에 맞게 토큰을 문자열로 변환합니다.
        return {"success": True, "token": token.to_jwt()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"토큰 생성 중 오류 발생: {str(e)}")