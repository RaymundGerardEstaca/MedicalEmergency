import React, { useState } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  TouchableOpacity, 
  StyleSheet, 
  Image,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { authAPI } from '../services/api';

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const navigation = useNavigation();

  const handleSignIn = async () => {
    setError(null);
    setSuccess(null);

    if (!email.trim() || !password.trim()) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);

    try {
      // Connect to the real backend API here!
      const data = await authAPI.login(email.trim(), password);

      // Successfully logged in
      setSuccess("Login successful");
      console.log("✅ Authenticated:", data);
      
      // Wait 1s and navigate just like before
      setTimeout(() => {
        navigation.replace('Dashboard');
      }, 1000);
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = () => {
    console.log("Sign in with Google");
  };

  const handleSignUp = () => {
    // Relying on the SignUp screen you built earlier
    navigation.navigate('SignUp');
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <View style={styles.card}>
        <Text style={styles.icon}>📷</Text>

        <Text style={styles.title}>Surveillance Camera</Text>

        <Text style={styles.subtitle}>Welcome back</Text>
        <Text style={styles.description}>
          Sign in to access your cameras
        </Text>

        {error ? <Text style={styles.errorText}>{error}</Text> : null}
        {success ? <Text style={styles.successText}>{success}</Text> : null}

        <TouchableOpacity style={styles.googleBtn} onPress={handleGoogleSignIn} disabled={loading}>
          <Image
            source={{ uri: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/512px-Google_%22G%22_Logo.svg.png" }}
            style={styles.googleIcon}
          />
          <Text style={styles.googleBtnText}>Continue with Google</Text>
        </TouchableOpacity>

        <View style={styles.dividerContainer}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>or continue with email</Text>
          <View style={styles.dividerLine} />
        </View>

        <View style={styles.form}>
          <Text style={styles.label}>Email Address</Text>
          <TextInput 
            style={styles.input}
            placeholder="you@example.com"
            value={email}
            onChangeText={(text) => {
              setEmail(text);
              if (error) setError(null);
            }}
            keyboardType="email-address"
            autoCapitalize="none"
            editable={!loading}
          />

          <Text style={styles.label}>Password</Text>
          <View style={styles.passwordContainer}>
            <TextInput 
              style={styles.passwordInput}
              placeholder="Enter your password"
              value={password}
              onChangeText={(text) => {
                setPassword(text);
                if(error) setError(null);
              }}
              secureTextEntry={!showPassword}
              editable={!loading}
            />
            <TouchableOpacity 
              style={styles.passwordToggle}
              onPress={() => setShowPassword(!showPassword)}
              disabled={loading}
            >
              <Text>{showPassword ? "👁️" : "👁️‍🗨️"}</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity 
            style={[styles.signInBtn, loading && styles.signInBtnDisabled]} 
            onPress={handleSignIn}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text style={styles.signInBtnText}>Sign In</Text>
            )}
          </TouchableOpacity>
        </View>

        <TouchableOpacity style={styles.signupContainer} onPress={handleSignUp} disabled={loading}>
          <Text style={styles.signupText}>
            Don't have an account? <Text style={styles.signupLink}>Sign up</Text>
          </Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
    padding: 20,
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  icon: {
    fontSize: 48,
    textAlign: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 4,
  },
  description: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
  },
  googleBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 24,
  },
  googleIcon: {
    width: 20,
    height: 20,
    marginRight: 8,
  },
  googleBtnText: {
    fontSize: 16,
    fontWeight: '500',
  },
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#ddd',
  },
  dividerText: {
    color: '#666',
    paddingHorizontal: 16,
    fontSize: 14,
  },
  form: {
    marginBottom: 24,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    fontSize: 16,
  },
  passwordContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    marginBottom: 24, // Changed back to original spacing
  },
  passwordInput: {
    flex: 1,
    padding: 12,
    fontSize: 16,
  },
  passwordToggle: {
    padding: 12,
  },
  signInBtn: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
  },
  signInBtnDisabled: {
    backgroundColor: '#99C7FF',
  },
  signInBtnText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  signupContainer: {
    alignItems: 'center',
  },
  signupText: {
    fontSize: 14,
    color: '#666',
  },
  signupLink: {
    color: '#007AFF',
    fontWeight: '600',
  },
  errorText: {
    color: '#FF3B30',
    backgroundColor: '#FFE5E5',
    padding: 10,
    borderRadius: 8,
    marginBottom: 16,
    textAlign: 'center',
    overflow: 'hidden',
    fontWeight: '500',
  },
  successText: {
    color: '#34C759',
    backgroundColor: '#E5F9E7',
    padding: 10,
    borderRadius: 8,
    marginBottom: 16,
    textAlign: 'center',
    overflow: 'hidden',
    fontWeight: '500',
  },
});
