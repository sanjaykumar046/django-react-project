import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useNavigate,
  Navigate,
} from "react-router-dom";
import axios from "axios";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api";

// Configure axios
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

// Spinner Component
function Spinner() {
  return <div className="loading-spinner"></div>;
}

// Alert Component
function Alert({ type, message, onClose }) {
  if (!message) return null;
  return (
    <div className={`alert alert-${type}`}>
      <span>{message}</span>
      {onClose && (
        <button onClick={onClose} className="alert-close">×</button>
      )}
    </div>
  );
}

// Protected Route
function ProtectedRoute({ children, allowedRoles }) {
  const user = JSON.parse(localStorage.getItem("user") || "null");
  const token = localStorage.getItem("access_token");

  if (!token || !user) {
    return <Navigate to="/" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

// Login Page
function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState({ type: "", message: "" });
  const navigate = useNavigate();

  useEffect(() => {
    if (localStorage.getItem("access_token")) {
      navigate("/dashboard");
    }
  }, [navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAlert({ type: "", message: "" });

    try {
      const response = await axios.post(`${API_URL}/login/`, {
        username,
        password,
      });

      localStorage.setItem("access_token", response.data.access);
      localStorage.setItem("refresh_token", response.data.refresh);
      localStorage.setItem("user", JSON.stringify(response.data.user));

      setAlert({ type: "success", message: "Login successful!" });
      setTimeout(() => navigate("/dashboard"), 500);
    } catch (error) {
      let message = "Login failed. Please try again.";
      if (error.response) {
        message = error.response.data?.error || error.response.data?.detail || message;
      } else if (error.request) {
        message = "Cannot connect to server. Please ensure Django is running on port 8000.";
      }
      setAlert({ type: "error", message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Project Management System</h2>
        <p className="login-subtitle">Sign in to continue</p>

        <Alert type={alert.type} message={alert.message} />

        <form onSubmit={handleLogin}>
          <input
            className="input"
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={loading}
          />
          <input
            className="input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? <><Spinner /> Logging in...</> : "Login"}
          </button>
        </form>

        <div className="test-credentials">
          <p>Test credentials: admin / admin123</p>
        </div>
      </div>
    </div>
  );
}

// Admin Dashboard
function AdminDashboard() {
  const [staff, setStaff] = useState([]);
  const [projects, setProjects] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState({ type: "", message: "" });
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [assignLoading, setAssignLoading] = useState(false);
  const [assignForm, setAssignForm] = useState({
    staff_id: "",
    project_id: "",
    project_password: "",
    notes: "",
  });

  const user = JSON.parse(localStorage.getItem("user"));

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [staffRes, projectsRes, assignmentsRes] = await Promise.all([
        axios.get(`${API_URL}/staff/`),
        axios.get(`${API_URL}/projects/`),
        axios.get(`${API_URL}/assignments/`),
      ]);

      setStaff(staffRes.data);
      setProjects(projectsRes.data);
      setAssignments(assignmentsRes.data);
    } catch (error) {
      setAlert({
        type: "error",
        message: error.response?.data?.error || "Failed to load data",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAssignProject = async (e) => {
    e.preventDefault();

    if (!assignForm.staff_id || !assignForm.project_id || !assignForm.project_password) {
      setAlert({ type: "error", message: "Please fill in all required fields" });
      return;
    }

    setAssignLoading(true);

    try {
      await axios.post(`${API_URL}/assign-project/`, {
        staff_id: parseInt(assignForm.staff_id),
        project_id: parseInt(assignForm.project_id),
        project_password: assignForm.project_password,
        notes: assignForm.notes || "",
      });

      setAlert({ type: "success", message: "Project assigned successfully!" });
      setShowAssignModal(false);
      setAssignForm({ staff_id: "", project_id: "", project_password: "", notes: "" });
      fetchData();
    } catch (error) {
      setAlert({
        type: "error",
        message: error.response?.data?.error || "Failed to assign project",
      });
    } finally {
      setAssignLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Admin Dashboard</h1>
          <p>Welcome back, {user.username}</p>
        </div>
      </div>

      <Alert type={alert.type} message={alert.message} onClose={() => setAlert({ type: "", message: "" })} />

      {loading ? (
        <div className="loading-container">
          <Spinner /> <span>Loading dashboard data...</span>
        </div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon blue">👥</div>
              <div className="stat-content">
                <h3>{staff.length}</h3>
                <p>Staff Members</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon green">📁</div>
              <div className="stat-content">
                <h3>{projects.length}</h3>
                <p>Active Projects</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon purple">📋</div>
              <div className="stat-content">
                <h3>{assignments.length}</h3>
                <p>Total Assignments</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon orange">🔓</div>
              <div className="stat-content">
                <h3>{assignments.filter(a => a.is_unlocked).length}</h3>
                <p>Unlocked Projects</p>
              </div>
            </div>
          </div>

          <div className="dashboard-content">
            <div className="section">
              <h2>Staff Members</h2>
              <div className="cards-container">
                {staff.length === 0 ? (
                  <p className="empty-message">No staff members found</p>
                ) : (
                  staff.map((s) => (
                    <div key={s.id} className="card">
                      <div className="card-avatar">{s.username.charAt(0).toUpperCase()}</div>
                      <h3>{s.username}</h3>
                      <p className="card-email">{s.email}</p>
                      <p className="card-meta">{s.first_name} {s.last_name}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="section">
              <h2>Projects</h2>
              <div className="cards-container">
                {projects.length === 0 ? (
                  <p className="empty-message">No projects found</p>
                ) : (
                  projects.map((p) => (
                    <div key={p.id} className="card project-card">
                      <h3>{p.name}</h3>
                      <p className="card-desc">{p.description}</p>
                      <div className="card-footer">
                        <span className="badge badge-info">
                          {p.assignments_count} assignments
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="section full-width">
              <div className="section-header">
                <h2>Assignments</h2>
                <button className="btn-primary" onClick={() => setShowAssignModal(true)}>
                  + Assign Project
                </button>
              </div>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Staff Member</th>
                      <th>Project</th>
                      <th>Status</th>
                      <th>Assigned Date</th>
                      <th>Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {assignments.length === 0 ? (
                      <tr>
                        <td colSpan="5" className="text-center">No assignments yet</td>
                      </tr>
                    ) : (
                      assignments.map((a) => (
                        <tr key={a.id}>
                          <td><strong>{a.staff_username}</strong></td>
                          <td>{a.project_name}</td>
                          <td>
                            <span className={`badge ${a.is_unlocked ? "badge-success" : "badge-warning"}`}>
                              {a.is_unlocked ? "Unlocked" : "Locked"}
                            </span>
                          </td>
                          <td>{new Date(a.assigned_at).toLocaleDateString()}</td>
                          <td>{a.notes || "-"}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      )}

      {showAssignModal && (
        <div className="modal-overlay" onClick={() => !assignLoading && setShowAssignModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Assign Project to Staff</h2>
            <form onSubmit={handleAssignProject}>
              <select
                className="input"
                value={assignForm.staff_id}
                onChange={(e) => setAssignForm({ ...assignForm, staff_id: e.target.value })}
                required
                disabled={assignLoading}
              >
                <option value="">Select Staff Member</option>
                {staff.map((s) => (
                  <option key={s.id} value={s.id}>{s.username} ({s.email})</option>
                ))}
              </select>

              <select
                className="input"
                value={assignForm.project_id}
                onChange={(e) => setAssignForm({ ...assignForm, project_id: e.target.value })}
                required
                disabled={assignLoading}
              >
                <option value="">Select Project</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>

              <input
                className="input"
                type="password"
                placeholder="Project Password"
                value={assignForm.project_password}
                onChange={(e) => setAssignForm({ ...assignForm, project_password: e.target.value })}
                required
                disabled={assignLoading}
              />

              <textarea
                className="input"
                placeholder="Notes (optional)"
                value={assignForm.notes}
                onChange={(e) => setAssignForm({ ...assignForm, notes: e.target.value })}
                rows="3"
                disabled={assignLoading}
              />

              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowAssignModal(false)} disabled={assignLoading}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={assignLoading}>
                  {assignLoading ? <><Spinner /> Assigning...</> : "Assign Project"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// Staff Dashboard
function StaffDashboard() {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState({ type: "", message: "" });
  const [unlockModal, setUnlockModal] = useState({ show: false, assignmentId: null });
  const [unlockPassword, setUnlockPassword] = useState("");
  const [unlockLoading, setUnlockLoading] = useState(false);

  const user = JSON.parse(localStorage.getItem("user"));

  useEffect(() => {
    fetchAssignments();
  }, []);

  const fetchAssignments = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/my-assignments/`);
      setAssignments(response.data);
    } catch (error) {
      setAlert({
        type: "error",
        message: error.response?.data?.error || "Failed to load assignments",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUnlock = async (e) => {
    e.preventDefault();
    setUnlockLoading(true);

    try {
      await axios.post(`${API_URL}/unlock-project/`, {
        assignment_id: unlockModal.assignmentId,
        project_password: unlockPassword,
      });

      setAlert({ type: "success", message: "Project unlocked successfully!" });
      setUnlockModal({ show: false, assignmentId: null });
      setUnlockPassword("");
      fetchAssignments();
    } catch (error) {
      setAlert({
        type: "error",
        message: error.response?.data?.error || "Invalid password",
      });
    } finally {
      setUnlockLoading(false);
    }
  };

  const lockedCount = assignments.filter(a => !a.is_unlocked).length;
  const unlockedCount = assignments.filter(a => a.is_unlocked).length;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Staff Dashboard</h1>
          <p>Welcome back, {user.username}</p>
        </div>
      </div>

      <Alert type={alert.type} message={alert.message} onClose={() => setAlert({ type: "", message: "" })} />

      {loading ? (
        <div className="loading-container">
          <Spinner /> <span>Loading your assignments...</span>
        </div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon blue">📋</div>
              <div className="stat-content">
                <h3>{assignments.length}</h3>
                <p>Total Assignments</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon green">🔓</div>
              <div className="stat-content">
                <h3>{unlockedCount}</h3>
                <p>Unlocked</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon orange">🔒</div>
              <div className="stat-content">
                <h3>{lockedCount}</h3>
                <p>Locked</p>
              </div>
            </div>
          </div>

          <div className="section full-width">
            <h2>My Assignments</h2>
            <div className="cards-container">
              {assignments.length === 0 ? (
                <p className="empty-message">No assignments yet</p>
              ) : (
                assignments.map((a) => (
                  <div key={a.id} className="card assignment-card">
                    <div className="card-header">
                      <h3>{a.project_name}</h3>
                      <span className={`badge ${a.is_unlocked ? "badge-success" : "badge-warning"}`}>
                        {a.is_unlocked ? "🔓 Unlocked" : "🔒 Locked"}
                      </span>
                    </div>
                    <div className="assignment-info">
                      <p><strong>Organization:</strong> {a.organization_name}</p>
                      <p><strong>Assigned by:</strong> {a.assigned_by_username}</p>
                      <p><strong>Date:</strong> {new Date(a.assigned_at).toLocaleDateString()}</p>
                      {a.notes && <p><strong>Notes:</strong> {a.notes}</p>}
                      {a.is_unlocked && (
                        <p><strong>Unlocked:</strong> {new Date(a.unlocked_at).toLocaleDateString()}</p>
                      )}
                    </div>
                    {!a.is_unlocked && (
                      <button
                        className="btn-primary mt-2"
                        onClick={() => setUnlockModal({ show: true, assignmentId: a.id })}
                      >
                        Unlock Project
                      </button>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}

      {unlockModal.show && (
        <div className="modal-overlay" onClick={() => !unlockLoading && setUnlockModal({ show: false, assignmentId: null })}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Unlock Project</h2>
            <p>Enter the project password to unlock</p>
            <form onSubmit={handleUnlock}>
              <input
                className="input"
                type="password"
                placeholder="Enter Project Password"
                value={unlockPassword}
                onChange={(e) => setUnlockPassword(e.target.value)}
                required
                disabled={unlockLoading}
                autoFocus
              />
              <div className="modal-actions">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setUnlockModal({ show: false, assignmentId: null })}
                  disabled={unlockLoading}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={unlockLoading}>
                  {unlockLoading ? <><Spinner /> Unlocking...</> : "Unlock"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// Dashboard Router
function Dashboard() {
  const user = JSON.parse(localStorage.getItem("user"));

  if (user.role === "admin" || user.role === "superuser") {
    return <AdminDashboard />;
  } else if (user.role === "staff") {
    return <StaffDashboard />;
  }

  return <div className="dashboard"><p>Unknown role</p></div>;
}

// Navbar
function Navbar() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "null");

  const handleLogout = () => {
    localStorage.clear();
    navigate("/");
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/dashboard">Project Management System</Link>
      </div>
      {user && (
        <div className="navbar-menu">
          <span className="navbar-user">
            {user.username} <span className="role-badge">({user.role})</span>
          </span>
          <button className="btn-logout" onClick={handleLogout}>
            Logout
          </button>
        </div>
      )}
    </nav>
  );
}

// Main App
export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <>
                <Navbar />
                <Dashboard />
              </>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}