import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";

export default function History({ user, onLogout }) {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => { fetchSessions(); }, []);

  const fetchSessions = async () => {
    try {
      const res = await API.get("/history/sessions");
      setSessions(res.data);
    } catch (e) { console.error(e); }
  };

  const loadSession = async (session) => {
    setLoading(true);
    setSelected(session);
    try {
      const res = await API.get(`/history/session/${session.id}/messages`);
      setMessages(res.data.messages);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const deleteSession = async (id, e) => {
    e.stopPropagation();
    if (!confirm("Delete this chat?")) return;
    await API.delete(`/history/session/${id}`);
    setSessions((prev) => prev.filter((s) => s.id !== id));
    if (selected?.id === id) { setSelected(null); setMessages([]); }
  };

  const reloadInChat = () => {
    // Store selected messages in sessionStorage and go to chat
    sessionStorage.setItem("reloadMessages", JSON.stringify(messages));
    sessionStorage.setItem("reloadSession", JSON.stringify(selected));
    navigate("/chat");
  };

  const filtered = sessions.filter((s) =>
    s.title.toLowerCase().includes(search.toLowerCase())
  );

  const formatDate = (dt) => new Date(dt).toLocaleString();

  return (
    <div className="history-page">
      {/* Navbar */}
      <div className="navbar">
        <div className="navbar-left">
          <span className="navbar-logo">🤖</span>
          <span className="navbar-title">Chat History</span>
        </div>
        <div className="navbar-right">
          <button className="nav-btn" onClick={() => navigate("/chat")}>
            💬 Back to Chat
          </button>
          <span className="navbar-user">👤 {user.username}</span>
          <button className="nav-btn-danger" onClick={() => { onLogout(); navigate("/login"); }}>
            Sign Out
          </button>
        </div>
      </div>

      <div className="history-layout">
        {/* Sessions list */}
        <div className="history-sidebar">
          <div className="history-search-box">
            <input
              className="history-search"
              placeholder="🔍 Search chats..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="sessions-count">
            {filtered.length} conversation{filtered.length !== 1 ? "s" : ""}
          </div>

          <div className="sessions-list">
            {filtered.length === 0 && (
              <div className="no-sessions">
                {search ? "No chats match your search." : "No chat history yet. Start a conversation!"}
              </div>
            )}
            {filtered.map((s) => (
              <div
                key={s.id}
                className={`session-item ${selected?.id === s.id ? "session-active" : ""}`}
                onClick={() => loadSession(s)}
              >
                <div className="session-title">{s.title}</div>
                <div className="session-meta">
                  <span>💬 {s.message_count} messages</span>
                  <span>{formatDate(s.updated_at)}</span>
                </div>
                {s.documents && (
                  <div className="session-docs">
                    📄 {s.documents.split(",").filter(Boolean).join(", ")}
                  </div>
                )}
                <button
                  className="session-delete"
                  onClick={(e) => deleteSession(s.id, e)}
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Message view */}
        <div className="history-main">
          {!selected && (
            <div className="history-empty">
              <div style={{ fontSize: 48 }}>📋</div>
              <div style={{ fontSize: 20, fontWeight: 600, marginTop: 12 }}>
                Select a conversation
              </div>
              <div style={{ color: "#858585", marginTop: 8 }}>
                Click any chat on the left to view messages
              </div>
            </div>
          )}

          {selected && (
            <>
              <div className="history-chat-header">
                <div>
                  <div className="history-chat-title">{selected.title}</div>
                  <div className="history-chat-meta">
                    {formatDate(selected.created_at)} · {messages.length} messages
                    {selected.documents && ` · 📄 ${selected.documents}`}
                  </div>
                </div>
                <button className="reload-btn" onClick={reloadInChat}>
                  ↩️ Reload in Chat
                </button>
              </div>

              <div className="history-messages">
                {loading && (
                  <div style={{ textAlign: "center", color: "#858585", padding: 40 }}>
                    Loading messages...
                  </div>
                )}
                {!loading && messages.map((m, i) => (
                  <div
                    key={i}
                    className={`h-message ${m.role === "user" ? "h-user" : "h-assistant"}`}
                  >
                    <div className="h-avatar">{m.role === "user" ? "👤" : "🤖"}</div>
                    <div className="h-content">
                      <div className="h-bubble">{m.content}</div>
                      {m.sources?.length > 0 && (
                        <div className="h-sources">
                          📚 {m.sources.filter(Boolean).join(", ")}
                        </div>
                      )}
                      <div className="h-time">
                        {new Date(m.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}