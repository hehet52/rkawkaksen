import { useEffect, useRef, useState } from "react";

function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isDrowsy, setIsDrowsy] = useState(false);

  useEffect(() => {
    const loadMediaPipe = async () => {
      const faceMeshScript = document.createElement("script");
      faceMeshScript.src =
        "https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/face_mesh.js";

      const cameraScript = document.createElement("script");
      cameraScript.src =
        "https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js";

      const drawingScript = document.createElement("script");
      drawingScript.src =
        "https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js";

      document.body.appendChild(faceMeshScript);
      document.body.appendChild(cameraScript);
      document.body.appendChild(drawingScript);

      drawingScript.onload = () => {
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
          const canvasElement = canvasRef.current;
          const canvasCtx = canvasElement.getContext("2d");

          canvasCtx.save();
          canvasCtx.clearRect(
            0,
            0,
            canvasElement.width,
            canvasElement.height
          );
          canvasCtx.translate(canvasElement.width, 0);
          canvasCtx.scale(-1, 1);

          canvasCtx.drawImage(
            results.image,
            0,
            0,
            canvasElement.width,
            canvasElement.height
          );

          if (results.multiFaceLandmarks) {
            const landmarks = results.multiFaceLandmarks[0];
            //눈 감김 감지
            const topEye = landmarks[159];
            const bottomEye = landmarks[145];

            //눈 높이 계산
            const eyeHeight = Math.abs(topEye.y - bottomEye.y);

            //졸음 판단
            if (eyeHeight < 0.015){
              setIsDrowsy(true);
            } else{
              setIsDrowsy(false);
            }



            for (const landmarks of results.multiFaceLandmarks) {
              window.drawConnectors(
                canvasCtx,
                landmarks,
                window.FACEMESH_TESSELATION,
                {
                  color: "#00FF00",
                  lineWidth: 1,
                }
              );
            }
          }

          canvasCtx.restore();
        });

        const camera = new window.Camera(videoRef.current, {
          onFrame: async () => {
            await faceMesh.send({ image: videoRef.current });
          },
          width: 640,
          height: 480,
        });

        camera.start();
      };
    };

    loadMediaPipe();
  }, []);

  return (
    <div style={{ textAlign: "center" }}>
      <h1>Face Landmark Test</h1>

      <video
        ref={videoRef}
        style={{ display: "none" }}
      />

      <canvas
        ref={canvasRef}
        width="640"
        height="480"
        style={{
          border: isDrowsy
          ? "8px solid red"
          : "3px solid black",
          borderRadius: "10px",
        }}
      />

      {isDrowsy && (
        <h2 style={{ color: "red" }}>
          DROWSY 😴
          </h2>
      )}
    </div>
  );
}

export default App;