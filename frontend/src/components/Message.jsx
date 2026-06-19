export default function Message({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`message ${isUser ? "user-message" : "assistant-message"}`}>
      <div className="message-avatar">
        {isUser ? "👤" : "🤖"}
      </div>
      <div className="message-content">
        <div className="message-bubble">
          <p className="message-text">{message.content}</p>
        </div>
        {message.sources?.length > 0 && (
          <div className="sources-bar">
            📚 Sources:{" "}
            {message.sources.map((s, i) => (
              <span key={i} className="source-tag">{s}</span>
            ))}
          </div>
        )}
        <div className="message-time">{message.timestamp}</div>
      </div>
    </div>
  );
}