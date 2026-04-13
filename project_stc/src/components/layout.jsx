import { useEffect, useState } from "react";
import { Outlet, NavLink, useLocation } from "react-router-dom";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

const Layout = () => {
  const [data, setData] = useState([]);
  const [showSessions, setShowSessions] = useState(false);

  const location = useLocation();

  const loadSessions = async () => {
    try {
      const response = await fetch(`${BASE_URL}/api/placements/sessions`);
      const result = await response.json();
      setData(result.data || []);
    } catch (err) {
      console.error("Failed to load sessions:", err);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  // Optional: Auto-hide sessions list on route change▲ ▼ ◭ ⧩ ⨻ Triangle Symbols

  useEffect(() => {
    setShowSessions(true);
    if (location.pathname.search('session') < 0) setShowSessions(false);
  }, [location.pathname]);

  return (
    <div className="content-container">
      <nav>
        <NavLink to="/" className={({ isActive }) => (isActive && !showSessions ? "active" : "")}>
          Home
        </NavLink>

        <span className={showSessions ? 'active' : ''}
          style={{ cursor: "pointer",}}
          onClick={()=>setShowSessions(true)}
        >
          {showSessions ? 'Sessions ▴':'Sessions ▾'}
        </span>

        {
            showSessions && (
                <div className="session-data">
                    {
                        data.map((item) => {
                        const date = new Date(item.session_date);
                        const year = date.getFullYear();
                        return (
                        <NavLink
                            key={year}
                            to={`/sessions/${year}`}
                            className={({ isActive }) => (isActive ? "active-item" : "")}
                            style={{ marginLeft: "20px", display: "block" }}
                        >
                            Session {year}
                        </NavLink>
                        );
                    })}
                </div>
            )
        }
          

        <NavLink to="/companies" className={({ isActive }) => (isActive && !showSessions ? "active" : "")}>
          Companies
        </NavLink>

        <NavLink to="/students" className={({ isActive }) => (isActive && !showSessions ? "active" : "")}>
          Students
        </NavLink>
      </nav>

      <div className="content-main">
        <Outlet />
      </div>
    </div>
  );
};

export default Layout;
