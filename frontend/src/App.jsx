import { useState, useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Login    from "./pages/Login";
import Register from "./pages/Register";
import Chat     from "./pages/Chat";
import History  from "./pages/History";

export default function App() {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("user");
    const token  = localStorage.getItem("token");
    if (stored && token) {
      setUser(JSON.parse(stored));
    }
    setLoading(false);
  }, []);

  const login = (userData, token) => {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  if (loading) return (
    <div style={{
      display: "flex", alignItems: "center",
      justifyContent: "center", height: "100vh",
      background: "#1e1e1e", color: "#d4d4d4", fontSize: 18
    }}>
      Loading...
    </div>
  );

  return (
    <Routes>
      <Route path="/login" element={
        user ? <Navigate to="/chat" /> : <Login onLogin={login} />
      } />
      <Route path="/register" element={
        user ? <Navigate to="/chat" /> : <Register onLogin={login} />
      } />
      <Route path="/chat" element={
        user ? <Chat user={user} onLogout={logout} /> : <Navigate to="/login" />
      } />
      <Route path="/history" element={
        user ? <History user={user} onLogout={logout} /> : <Navigate to="/login" />
      } />
      <Route path="*" element={
        <Navigate to={user ? "/chat" : "/login"} />
      } />
    </Routes>
  );
}