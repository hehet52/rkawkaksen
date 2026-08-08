from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import joblib
import numpy as np

app = FastAPI()

# 1. 서버 시작 시 AI 모델 및 스케일러 한 번만 불러오기
try:
    model = joblib.load("drowsiness_model.pkl")  # 전달받은 파일명과 동일해야 합니다.
    scaler = joblib.load("scaler.pkl")
    print("✅ AI 모델 및 스케일러 로드 완료")
except Exception as e:
    print(f"❌ 모델/스케일러 로드 실패: {e}")

@app.websocket("/ws/ear")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🟢 클라이언트(프론트엔드) 연결됨")
    
    try:
        while True:
            # 2. 프론트엔드에서 4개의 변수가 담긴 리스트(배열)를 수신
            # 예시: 프론트에서 [0.25, 0.12, 0.05, 0.88] 형태로 보낸다고 가정
            data = await websocket.receive_json()
            
            # 수신된 데이터가 4개의 값을 가진 리스트인지 확인
            if isinstance(data, list) and len(data) == 4:
                
                # 3. 모델 입력을 위해 2차원 배열로 변환 후 Scaler 적용
                input_data = np.array([data])
                scaled_data = scaler.transform(input_data)
                
                # 4. 모델 예측 (0: 정상, 1: 졸음)
                prediction = model.predict(scaled_data)[0]
                result_status = "drowsy" if prediction == 1 else "normal"
                
                # 5. 프론트엔드로 판별 결과 반환
                await websocket.send_json({
                    "status": result_status,
                    "input_values": data  # 잘 들어왔는지 확인용
                })
            else:
                # 데이터가 4개가 아닐 경우 에러 메시지 반환
                await websocket.send_json({
                    "error": "잘못된 데이터 형식입니다. 4개의 수치가 배열 형태로 들어와야 합니다.",
                    "received": data
                })

    except WebSocketDisconnect:
        print("🔴 클라이언트 연결 종료")
    except Exception as e:
        print(f"❌ 웹소켓 처리 중 오류 발생: {e}")