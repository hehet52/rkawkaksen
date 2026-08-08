import joblib
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

# 모델 및 스케일러 미리 불러오기 (서버 시작 시 실행)
try:
    model = joblib.load("random_forest_model.pkl")
    scaler = joblib.load("scaler.pkl")
    print("AI 모델 및 스케일러 로드 완료")
except Exception as e:
    print(f"모델/스케일러 로드 실패: {e}")

@app.websocket("/ws/ear")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("클라이언트(프론트엔드) 연결됨")
    
    try:
        while True:
            # 1. 프론트엔드에서 실시간 전달한 EAR 수치 수신
            data = await websocket.receive_text()
            ear_value = float(data)
            
            # 2. Scaler 정규화 변환 (입력 형태 맞춤)
            input_data = np.array([[ear_value]])
            scaled_data = scaler.transform(input_data)
            
            # 3. 모델 예측 (0: 정상, 1: 졸음)
            prediction = model.predict(scaled_data)[0]
            result_status = "drowsy" if prediction == 1 else "normal"
            
            # 4. 프론트엔드로 판별 결과 반환
            await websocket.send_json({
                "ear": ear_value,
                "status": result_status
            })

    except WebSocketDisconnect:
        print("클라이언트 연결 종료")
    except Exception as e:
        print(f"오류 발생: {e}")