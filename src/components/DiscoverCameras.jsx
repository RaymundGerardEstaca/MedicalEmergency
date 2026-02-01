import { useState } from "react";
import "./DiscoverCameras.css";
import { discoveryAPI } from "../services/api";

function DiscoverCameras({ onBack }) {
  const [scanMode, setScanMode] = useState("bluetooth");
  const [discoveredDevices, setDiscoveredDevices] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState("");

  const pairingSteps = [
    "Power on your camera device",
    "Press and hold the pairing button for 5 seconds",
    "Wait for the LED to blink rapidly",
    "Select the device from the list above"
  ];

  const handleScan = async () => {
    setIsScanning(true);
    setError("");
    setDiscoveredDevices([]);
    
    try {
      // Call the scan API with the selected mode
      const devices = await discoveryAPI.scanDevices(scanMode);
      console.log("Devices found:", devices);
      setDiscoveredDevices(devices || []);
    } catch (err) {
      setError(err.message || "Scan failed");
      console.error("Scan error:", err);
    } finally {
      setIsScanning(false);
    }
  };

  const handlePair = async (device) => {
    try {
      // Call the pair API
      const result = await discoveryAPI.pairDevice(device.id, scanMode);
      console.log("Pairing result:", result);
      // In a real app, you'd add this camera to the user's list
      alert(`Successfully paired with ${device.name}`);
    } catch (err) {
      setError(err.message || "Pairing failed");
      console.error("Pairing error:", err);
    }
  };

  return (
    <div className="discover-container">
      <div className="discover-header">
        <button className="discover-back" onClick={onBack}>←</button>
        <h1 className="discover-title">Discover Cameras</h1>
        <div style={{ width: "24px" }}></div>
      </div>

      <div className="discover-content">
        <p className="discover-subtitle">Scanning for available devices via Bluetooth or WiFi hotspot</p>

        {error && <div style={{ color: '#d32f2f', fontSize: '14px', marginBottom: '12px', textAlign: 'center' }}>{error}</div>}

        <div className="discover-mode-toggle">
          <button 
            className={`discover-mode-btn ${scanMode === "bluetooth" ? "active" : ""}`}
            onClick={() => setScanMode("bluetooth")}
            disabled={isScanning}
          >
            Bluetooth
          </button>
          <button 
            className={`discover-mode-btn ${scanMode === "wifi" ? "active" : ""}`}
            onClick={() => setScanMode("wifi")}
            disabled={isScanning}
          >
            WiFi Hotspot
          </button>
        </div>

        <div className="discover-section">
          <div className="discover-section-header">
            <h2 className="discover-section-title">Discovered Devices ({discoveredDevices.length})</h2>
            <button 
              className="discover-scan-again"
              onClick={handleScan}
              disabled={isScanning}
            >
              {isScanning ? "Scanning..." : "Scan Again"}
            </button>
          </div>

          {discoveredDevices.length === 0 ? (
            <div className="discover-empty-state">
              <div className="discover-empty-icon">📡</div>
              <h3 className="discover-empty-title">No devices found</h3>
              <p className="discover-empty-text">Ensure your camera is in pairing mode</p>
              <button 
                className="discover-retry-btn"
                onClick={handleScan}
                disabled={isScanning}
              >
                {isScanning ? "Scanning..." : "Retry Scan"}
              </button>
            </div>
          ) : (
            <div className="discover-devices-list">
              {discoveredDevices.map((device, index) => (
                <div key={index} className="discover-device-item">
                  <div className="discover-device-info">
                    <span className="discover-device-name">{device.name}</span>
                    <span className="discover-device-signal">{device.signal}</span>
                  </div>
                  <button 
                    className="discover-device-pair"
                    onClick={() => handlePair(device)}
                  >
                    Pair
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="discover-section">
          <h2 className="discover-section-title">Pairing Instructions</h2>
          <div className="discover-instructions">
            {pairingSteps.map((step, index) => (
              <div key={index} className="discover-instruction-item">
                <div className="discover-instruction-number">{index + 1}</div>
                <p className="discover-instruction-text">{step}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default DiscoverCameras;
