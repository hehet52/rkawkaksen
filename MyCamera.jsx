import { useEffect, useRef } from "react";

function MyCamera({ onStatusChange }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const csvDataRef = useRef([]);
  const closedEyeStartRef = useRef(null);
  const socketRef = useRef(null);

  useEffect(() => {
    socketRef.current = new WebSocket(
      "ws://10.103.20.15:8000/ws/drowsiness/test_user"
    );

    socketRef.current.onopen = () => {
      console.log("웹소켓 연결 성공 😎");
    };

    socketRef.current.onmessage = (event) => {
      const receivedStatus = event.data;
      console.log("백엔드에서 받은 status:", receivedStatus);

      onStatusChange(receivedStatus);
    };

    socketRef.current.onerror = (error) => {
      console.log("웹소켓 에러:", error);
    };

    socketRef.current.onclose = () => {
      console.log("웹소켓 연결 종료");
    };

    const loadScript = (src) =>
      new Promise((resolve) => {
        const script = document.createElement("script");
        script.src = src;
        script.onload = resolve;
        document.body.appendChild(script);
      });

    async function startMediaPipe() {
      await loadScript(
        "https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/face_mesh.js"
      );
      await loadScript(
        "https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"
      );
      await loadScript(
        "https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js"
      );

      const faceMesh = new window.FaceMesh({
        locateFile: (file) =>
          `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`,
      });

      faceMesh.setOptions({
        maxNumFaces: 1,
        refineLandmarks: true,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });

      faceMesh.onResults((results) => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");

        ctx.save();
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

        let status = "집중중";
        let eyeHeight = "";

        if (results.multiFaceLandmarks) {
          const landmarks = results.multiFaceLandmarks[0];

          window.drawConnectors(ctx, landmarks, window.FACEMESH_TESSELATION, {
            color: "#00ff00",
            lineWidth: 1,
          });

          const topEye = landmarks[159];
          const bottomEye = landmarks[145];

          eyeHeight = Math.abs(topEye.y - bottomEye.y);

          if (eyeHeight < 0.015) {
            if (!closedEyeStartRef.current) {
              closedEyeStartRef.current = Date.now();
            }

            const closedTime = Date.now() - closedEyeStartRef.current;

            if (closedTime >= 5000) {
              status = "졸음";
            }
          } else {
            closedEyeStartRef.current = null;
          }

          csvDataRef.current.push({
            time: Date.now(),
            eyeHeight,
            status,
          });

          onStatusChange(status);

          console.log("백엔드로 보낼 status:", status);

          if (
            socketRef.current &&
            socketRef.current.readyState === WebSocket.OPEN
          ) {
            socketRef.current.send(status);
          }
        }

        ctx.restore();
      });

      const camera = new window.Camera(videoRef.current, {
        onFrame: async () => {
          await faceMesh.send({
            image: videoRef.current,
          });
        },
        width: 640,
        height: 480,
      });

      camera.start();
    }

    startMediaPipe();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [onStatusChange]);

  return (
    <div>
      <video ref={videoRef} style={{ display: "none" }} />

      <canvas
        ref={canvasRef}
        width={640}
        height={480}
        style={{
          width: "100%",
          height: "220px",
          borderRadius: "15px",
          transform: "scaleX(-1)",
        }}
      />

      <button
        onClick={() => {
          const csv =
            "time,eyeHeight,status\n" +
            csvDataRef.current
              .map((row) => row.time + "," + row.eyeHeight + "," + row.status)
              .join("\n");

          const blob = new Blob([csv], {
            type: "text/csv",
          });

          const url = URL.createObjectURL(blob);

          const a = document.createElement("a");
          a.href = url;
          a.download = "my_eye_data.csv";
          a.click();
        }}
        style={{
          marginTop: "10px",
          padding: "8px 14px",
          borderRadius: "8px",
          border: "none",
          cursor: "pointer",
        }}
      >
        CSV 다운로드
      </button>
    </div>
  );
}

export default MyCamera;
