import { useState } from "react";
import "./App.css";
import Dashboard from "./components/Dashboard";
import DiscoverCameras from "./components/DiscoverCameras";
import SignUp from "./components/SignUp";
import { authAPI } from "./services/api";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentPage, setCurrentPage] = useState("login"); // login, signup, dashboard, discover
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSignIn = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    
    try {
      // Call the login API
      const result = await authAPI.login(email, password);
      console.log("Login successful:", result);
      
      setIsLoggedIn(true);
      setCurrentPage("dashboard");
      setEmail("");
      setPassword("");
    } catch (err) {
      setError(err.message || "Login failed");
      console.error("Login error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    setError("");
    
    try {
      // In a real app, you'd get the Google token from Google SDK
      const googleToken = "google_token_from_sdk";
      const result = await authAPI.googleSignIn(googleToken);
      console.log("Google sign in successful:", result);
      
      setIsLoggedIn(true);
      setCurrentPage("dashboard");
    } catch (err) {
      setError(err.message || "Google sign in failed");
      console.error("Google sign in error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignUp = () => {
    setCurrentPage("signup");
    setError("");
  };

  const handleBackToLogin = () => {
    setCurrentPage("login");
    setError("");
  };

  const handleLogout = () => {
    authAPI.logout();
    setIsLoggedIn(false);
    setCurrentPage("login");
    setEmail("");
    setPassword("");
    setShowPassword(false);
  };

  const handleAddCamera = () => {
    setCurrentPage("discover");
  };

  const handleBackToDiscovery = () => {
    setCurrentPage("dashboard");
  };

  // If user is logged in, show dashboard or discover page
  if (isLoggedIn) {
    if (currentPage === "discover") {
      return <DiscoverCameras onBack={handleBackToDiscovery} />;
    }
    return <Dashboard onLogout={handleLogout} onAddCamera={handleAddCamera} />;
  }

  // Show signup page
  if (currentPage === "signup") {
    return <SignUp onSignUpSuccess={handleBackToLogin} onBackToLogin={handleBackToLogin} />;
  }

  // Show login page (default)

  return (
    <div className="container">
      <div className="card">
        <div className="icon">📷</div>

        <h1 className="title">Surveillance Camera</h1>

        <h2 className="subtitle">Welcome back</h2>
        <p className="description">
          Sign in to access your cameras
        </p>

        {error && <div style={{ color: '#d32f2f', fontSize: '14px', marginBottom: '12px' }}>{error}</div>}

        <button 
          className="google-btn" 
          onClick={handleGoogleSignIn}
          disabled={isLoading}
        >
          <img
            src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/512px-Google_%22G%22_Logo.svg.png"
            alt="Google"
          />
          Continue with Google
        </button>

        <div className="divider">
          <span>or continue with email</span>
        </div>

        <form onSubmit={handleSignIn}>
          <label>Email Address</label>
          <input 
            type="email" 
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <label>Password</label>
          <div className="password-field">
            <input 
              type={showPassword ? "text" : "password"} 
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button 
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? "👁️" : "👁️‍🗨️"}
            </button>
          </div>

          <button type="submit" className="signin-btn" disabled={isLoading}>
            {isLoading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p className="signup">
          Don't have an account? <span onClick={handleSignUp}>Sign up</span>
        </p>
      </div>
    </div>
  );
}

export default App;
