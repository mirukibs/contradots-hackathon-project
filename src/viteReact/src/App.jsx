import { BrowserRouter, Routes, Route } from "react-router-dom";

import Welcome from "./pages/Welcome";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Activities from "./pages/Activities";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Welcome / Landing */}
        <Route path="/" element={<Welcome />} />

        {/* Auth */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/activities" element={<Activities />} />

      </Routes>
    </BrowserRouter>
  );
}
