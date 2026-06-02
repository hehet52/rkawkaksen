import "./App.css";
import UserCard from "./components/UserCard";
import { useState, useEffect } from "react";

function App() {
  const [myStatus, setMyStatus] =
    useState("집중중");

  useEffect(() => {
    const timer = setTimeout(() => {
      setMyStatus("졸음");
    }, 5000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#f5f5f5",
        padding: "40px",
      }}
    >
      <h1
        style={{
          textAlign: "center",
          marginBottom: "40px",
        }}
      >
        💤 졸음 감지 캠스터디
      </h1>

      <div
        style={{
          textAlign: "center",
          marginBottom: "20px",
        }}
      >
        <button
          onClick={() =>
            setMyStatus("졸음")
          }
          style={{
            padding: "10px 20px",
            marginRight: "10px",
            borderRadius: "10px",
            border: "none",
            cursor: "pointer",
          }}
        >
          졸음 테스트
        </button>

        <button
          onClick={() =>
            setMyStatus("집중중")
          }
          style={{
            padding: "10px 20px",
            borderRadius: "10px",
            border: "none",
            cursor: "pointer",
          }}
        >
          집중 테스트
        </button>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "30px",
        }}
      >
        <UserCard
          name="다람쥐"
          status={myStatus}
          isMine={true}
          onStatusChange={setMyStatus}
        />

        <UserCard
          name="병아리"
          status="졸음"
        />

        <UserCard
          name="토끼"
          status="집중중"
        />

        <UserCard
          name="곰"
          status="하품중"
        />
      </div>
    </div>
  );
}

export default App;