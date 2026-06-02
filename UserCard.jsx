import MyCamera from "./MyCamera";

function UserCard({ name, status, isMine, onStatusChange }) {
  return (
    <div
      style={{
        backgroundColor: "white",
        borderRadius: "20px",
        padding: "20px",
        boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
        border:
          status === "졸음"
            ? "4px solid red"
            : status === "하품중"
            ? "4px solid orange"
            : "4px solid green",
      }}
    >
      {isMine ? (
        <MyCamera onStatusChange={onStatusChange} />
      ) : (
        <div
          style={{
            height: "220px",
            backgroundColor: "#ddd",
            borderRadius: "15px",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontSize: "50px",
            marginBottom: "15px",
          }}
        >
          📷
        </div>
      )}

      <h2>{name}</h2>
      <p>{status}</p>

      {status === "졸음" && (
        <div
          style={{
            marginTop: "10px",
            color: "red",
            fontWeight: "bold",
            fontSize: "24px",
          }}
        >
          DROWSY 😴
        </div>
      )}
    </div>
  );
}

export default UserCard;