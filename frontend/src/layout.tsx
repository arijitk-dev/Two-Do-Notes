import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";

export default function Layout() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("two-do-user") || "null");
  return <div className="app-shell"><aside className="sidebar"><Link to="/dashboard" className="brand"><span className="brand-mark">2</span><span>Two Do<br/><em>Notes</em></span></Link><nav><NavLink to="/dashboard">Overview</NavLink><NavLink to="/todos">Todos</NavLink><NavLink to="/calendar">Calendar</NavLink><NavLink to="/notes">Notes</NavLink><NavLink to="/settings">Settings</NavLink></nav><div className="sidebar-footer"><div className="avatar">{user?.name?.[0]?.toUpperCase() || "U"}</div><div className="user-label"><strong>{user?.name || "Account"}</strong><small>{user?.email}</small></div><button className="text-button" aria-label="Log out" onClick={() => { localStorage.clear(); navigate("/login"); }}>↪</button></div></aside><main className="main-content"><Outlet /></main></div>;
}
