import { useState } from "react";
import { Link } from "react-router-dom";
import API from "../api";

export default function Register({ onLogin }) {
  const [form, setForm]     = useState({ username: "", email: "", password: "", confirm: "" });
  const [error, setError]   = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Frontend validation
    if (form.username.trim().length < 3) {
      setError("Username must be at least 3 characters.");
      return;
    }
    if (!form.email.includes("@")) {
      setError("Please enter a valid email.");
      return;
    }
    if (form.password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    if (form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const res = await API.post("/auth/register", {
        username: form.username.trim(),
        email:    form.email.trim(),
        password: form.password,
      });

      // Success — log user in immediately
      onLogin(
        { username: res.data.username, email: res.data.email },
        res.data.access_token
      );

    } catch (err) {
      console.error("Register error full:", err);
      console.error("Register error response:", err.response);
      console.error("Register error data:", err.response?.data);

      if (err.response) {
        // Server responded with error
        const detail = err.response.data?.detail;
        if (typeof detail === "string") {
          setError(detail);
        } else if (Array.isArray(detail)) {
          setError(detail[0]?.msg || "Validation error.");
        } else {
          setError(`Server error: ${err.response.status}`);
        }
      } else if (err.request) {
        // No response at all
        setError("Cannot reach server. Is the backend running on port 8000?");
      } else {
        setError("Unexpected error: " + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">🤖</div>
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-subtitle">Join Enterprise Chatbot</p>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              className="form-input"
              type="text"
              placeholder="Choose a username (min 3 chars)"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              className="form-input"
              type="email"
              placeholder="your@email.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              className="form-input"
              type="password"
              placeholder="Min 6 characters"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <input
              className="form-input"
              type="password"
              placeholder="Repeat your password"
              value={form.confirm}
              onChange={(e) => setForm({ ...form, confirm: e.target.value })}
              required
            />
          </div>

          {error && (
            <div className="auth-error">
              ❌ {error}
            </div>
          )}

          <button
            className="auth-btn"
            type="submit"
            disabled={loading}
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="auth-link">
          Already have an account?{" "}
          <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}