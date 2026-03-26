import { Navigate, Route, Routes } from "react-router-dom";
import { ShellBackground } from "./components/ShellBackground";
import { ConsolePage } from "./pages/ConsolePage";
import { HomePage } from "./pages/HomePage";

export default function App() {
  return (
    <div className="app-shell">
      <ShellBackground />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/console" element={<ConsolePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
