import { Link } from "react-router-dom";
import "./welcome.css";

export default function Welcome() {
  return (
    <>
      <header className="header">
        <span className="logo">
          <b>Credora</b>
        </span>
        <span></span>
      </header>

      <main className="splash-page">
        <span className="glow"></span>

        <h1>Welcome To Credora</h1>
        <p>A Web3 powered Social Credit Score System</p>

        <div className="splash-buttons">
          <Link to="/register">
            <button className="splash-btn">Register</button>
          </Link>

          <Link to="/login">
            <button className="splash-btn outline">Login</button>
          </Link>
        </div>
      </main>
    </>
  );
}
