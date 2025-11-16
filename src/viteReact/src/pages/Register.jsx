import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../api/auth";
import "./register.css";

export default function Register() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "MEMBER",
  });
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

    const result = await registerUser(form);
    setLoading(false);

    if (result.error) {
      setError(result.error);
    } else {
      // If backend returns token
      const { data } = result;
      if (data.token) {
        localStorage.setItem("token", data.token);
      }
      // If there's a user ID or name, you can store it or do whatever
      // Then redirect to dashboard or some protected route
      navigate("/dashboard"); // change this to where you want
    }
  };

  return (
    <>
      <header className="header">
        <span className="logo">
          <b>Credora</b>
        </span>
      </header>

      <main className="signup">
        <form className="card" onSubmit={handleSubmit}>
          <h2>Signup</h2>

          <input
            type="text"
            name="name"
            placeholder="Full name"
            value={form.name}
            onChange={handleChange}
          />

          <input
            type="email"
            name="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
          />

          <input
            type="password"
            name="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
          />

          <select name="role" value={form.role} onChange={handleChange}>
            <option value="MEMBER">Member</option>
            <option value="LEAD">Lead</option>
          </select>

          {error && (
            <div className="error">
              {/* Display a simple error structure; adjust based on your backend */}
              <b>Error:</b> {JSON.stringify(error)}
            </div>
          )}

          <div className="splash-buttons">
            <button type="submit" disabled={loading}>
              {loading ? "Creating..." : "Create Account"}
            </button>

            <Link to="/login">
              <button type="button" className="splash-btn outline">
                Login
              </button>
            </Link>
          </div>
        </form>
      </main>
    </>
  );
}
