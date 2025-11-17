import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginUser } from "../api/auth";
import "./register.css";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const result = await loginUser(form);
    setLoading(false);

    if (result.error) {
      setError(result.error);
    } else {
      // result is the direct response from the API
      console.log("Login successful:", result);
      
      // Store token - it should already be stored by authAPI.login()
      if (result.token) {
        localStorage.setItem("token", result.token);
        // Also store user info for easy access
        if (result.user_id) {
          localStorage.setItem("user_id", result.user_id);
        }
        if (result.email) {
          localStorage.setItem("user_email", result.email);
        }
      }
      
      // redirect to dashboard
      navigate("/dashboard");
    }
  };

  return (
    <>
      <header className="header">
        <span className="logo">
          <b>Credora</b>
        </span>
      </header>

      <main className="login">
        <form className="card" onSubmit={handleSubmit}>
          <h2>Login</h2>

          <input
            name="email"
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
          />

          <input
            name="password"
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
          />

          {error && (
            <div className="error">
              <b>Error:</b> {JSON.stringify(error)}
            </div>
          )}

          <div className="splash-buttons">
            <button type="submit" disabled={loading}>
              {loading ? "Logging in..." : "Login"}
            </button>

            <Link to="/register">
              <button type="button" className="splash-btn outline">
                Signup
              </button>
            </Link>
          </div>
        </form>
      </main>
    </>
  );
}
