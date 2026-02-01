import { useState, useEffect } from "react";
import "./Dashboard.css";
import { cameraAPI, statsAPI } from "../services/api";

function Dashboard({ onLogout, onAddCamera }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [cameras, setCameras] = useState([]);
  const [stats, setStats] = useState({
    totalCameras: 0,
    online: 0,
    offline: 0,
    alerts: 0
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  // Fetch cameras and stats when component mounts
  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError("");
    
    try {
      // Fetch cameras and stats from API
      const camerasData = await cameraAPI.getCameras();
      const statsData = await statsAPI.getStats();
      
      setCameras(camerasData || []);
      setStats({
        totalCameras: statsData?.totalCameras || 0,
        online: statsData?.online || 0,
        offline: statsData?.offline || 0,
        alerts: statsData?.alerts || 0
      });
    } catch (err) {
      setError(err.message || "Failed to load dashboard data");
      console.error("Dashboard error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    setMenuOpen(false);
    onLogout();
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1 className="dashboard-title">My Cameras</h1>
        <div className="dashboard-menu-wrapper">
          <button 
            className="dashboard-menu"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Menu"
          >
            ⋮
          </button>
          {menuOpen && (
            <div className="dashboard-menu-dropdown">
              <button className="dashboard-menu-item" onClick={handleLogout}>
                Logout
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="dashboard-stats">
        <div className="dashboard-stat-card">
          <p className="dashboard-stat-label">TOTAL CAMERAS</p>
          <div className="dashboard-stat-value">{String(stats.totalCameras).padStart(2, '0')}</div>
        </div>
        <div className="dashboard-stat-card">
          <p className="dashboard-stat-label">ONLINE</p>
          <div className="dashboard-stat-value">{String(stats.online).padStart(2, '0')}</div>
        </div>
        <div className="dashboard-stat-card">
          <p className="dashboard-stat-label">OFFLINE</p>
          <div className="dashboard-stat-value">{String(stats.offline).padStart(2, '0')}</div>
        </div>
        <div className="dashboard-stat-card">
          <p className="dashboard-stat-label">ALERTS</p>
          <div className="dashboard-stat-value">{String(stats.alerts).padStart(2, '0')}</div>
        </div>
      </div>

      <h2 className="dashboard-section-title">Your Cameras</h2>

      <div className="dashboard-cameras">
        {error && <div style={{ color: '#d32f2f', fontSize: '14px', marginBottom: '12px', textAlign: 'center' }}>{error}</div>}
        
        {isLoading ? (
          <div className="dashboard-empty-state">
            <div className="dashboard-empty-icon">⏳</div>
            <h3 className="dashboard-empty-title">Loading...</h3>
          </div>
        ) : cameras.length === 0 ? (
          <div className="dashboard-empty-state">
            <div className="dashboard-empty-icon">📷</div>
            <h3 className="dashboard-empty-title">No cameras yet</h3>
            <p className="dashboard-empty-text">Add your first camera to start monitoring</p>
            <button className="dashboard-add-btn" onClick={onAddCamera}>
              Add Your First Camera
            </button>
          </div>
        ) : (
          <div className="dashboard-cameras-list">
            {cameras.map((camera, index) => (
              <div key={index} className="dashboard-camera-card">
                <h3>{camera.name}</h3>
                <p className="dashboard-camera-status">{camera.status}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
