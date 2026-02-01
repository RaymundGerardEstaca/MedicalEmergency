import { useState } from "react";
import "./Login.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSignIn = (e) => {
    e.preventDefault();
    console.log("Sign in with:", { email, password });
  };

  const handleGoogleSignIn = () => {
    console.log("Sign in with Google");
  };

  const handleSignUp = () => {
    console.log("Go to sign up");
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-icon">📷</div>

        <h1 className="login-title">Surveillance Camera</h1>

        <h2 className="login-subtitle">Welcome back</h2>
        <p className="login-description">
          Sign in to access your cameras
        </p>

        <button className="login-google-btn" onClick={handleGoogleSignIn}>
          <img
            src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/512px-Google_%22G%22_Logo.svg.png"
            alt="Google"
          />
          Continue with Google
        </button>

        <div className="login-divider">
          <span>or continue with email</span>
        </div>

        <form className="login-form" onSubmit={handleSignIn}>
          <label>Email Address</label>
          <input 
            type="email" 
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <label>Password</label>
          <div className="login-password-field">
            <input 
              type={showPassword ? "text" : "password"} 
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button 
              type="button"
              className="login-password-toggle"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? "👁️" : "👁️‍🗨️"}
            </button>
          </div>

          <button type="submit" className="login-signin-btn">Sign In</button>
        </form>

        <p className="login-signup">
          Don't have an account? <span onClick={handleSignUp}>Sign up</span>
        </p>
      </div>
    </div>
  );
}

export default Login;
