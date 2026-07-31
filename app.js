const videoElement = document.getElementById('my-webcam');

// 1. 두 점 사이의 거리를 구하는 수학 함수
function getDistance(p1, p2) {
  return Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2));
}

// 2. 눈 감김 비율(EAR: Eye Aspect Ratio) 계산 함수
function calculateEAR(landmarks, eyeIndices) {
  // eyeIndices: [top1, bottom1, top2, bottom2, left, right]
  const p2_p6 = getDistance(landmarks[eyeIndices[0]], landmarks[eyeIndices[1]]);
  const p3_p5 = getDistance(landmarks[eyeIndices[2]], landmarks[eyeIndices[3]]);
  const p1_p4 = getDistance(landmarks[eyeIndices[4]], landmarks[eyeIndices[5]]);

  // EAR 공식
  const ear = (p2_p6 + p3_p5) / (2.0 * p1_p4);
  return ear;
}

// MediaPipe 얼굴 좌표 중 눈 주변 점 인덱스 번호
const LEFT_EYE = [385, 380, 387, 373, 362, 263];
const RIGHT_EYE = [160, 144, 158, 153, 33, 133];

// 3. MediaPipe FaceMesh 인스턴스 생성
const faceMesh = new FaceMesh({
  locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
});

faceMesh.setOptions({
  maxNumFaces: 1,
  refineLandmarks: true,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5
});

// 4. 얼굴 인식이 완료될 때마다 계속 실행되는 함수
faceMesh.onResults((results) => {
  if (results.multiFaceLandmarks && results.multiFaceLandmarks[0]) {
    const landmarks = results.multiFaceLandmarks[0];

    // 양쪽 눈 EAR 계산 후 평균값 구하기
    const leftEAR = calculateEAR(landmarks, LEFT_EYE);
    const rightEAR = calculateEAR(landmarks, RIGHT_EYE);
    const avgEAR = (leftEAR + rightEAR) / 2.0;

    // 콘솔 창에 실시간 수치 출력 (F12 누르면 보임)
    console.log(`[EAR 분석 데이터] 현재 수치: ${avgEAR.toFixed(3)}`);

    // 간단 테스트용: 수치가 0.18 이하로 내려가면 (눈을 뜨지 않거나 감으면) 화면 텍스트 임시 변경
    const statusBadge = document.getElementById('my-status');
    if (avgEAR < 0.18) {
      statusBadge.innerText = '🚨 졸음 감지';
      statusBadge.className = 'status-badge drowsy';
    } else {
      statusBadge.innerText = '🟢 정상';
      statusBadge.className = 'status-badge focus';
    }

    // 💡 백엔드(WebSocket)로 전송할 데이터를 객체 형태로 준비해둡니다.
    // const dataToSend = { ear: avgEAR, timestamp: Date.now() };
  }
});

// 5. 웹캠 연결 및 실행
const camera = new Camera(videoElement, {
  onFrame: async () => {
    await faceMesh.send({ image: videoElement });
  },
  width: 640,
  height: 480
});

camera.start();