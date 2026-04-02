import React, { useState } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  TouchableOpacity, 
  StyleSheet, 
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform 
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { mockApi } from '../services/mockApi';

export default function Login() {
  const navigation = useNavigation();
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const validateInput = () => {
    if (!email.trim() || !password.trim()) {
      setError('Please fill in all fields');
      return false;
    }
    
    // Basic email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError('Please enter a valid email address');
      return false;
    }

    // Optional: basic password length check
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return false;
    }

    return true;
  };

  const handleAuth = async () => {
    // Reset states
    setError(null);
    setSuccess(null);

    // Validate inputs before calling API
    if (!validateInput()) {
      return;
    }

    setLoading(true);

    try {
      let response;
      if (isLoginMode) {
        response = await mockApi.login(email.trim(), password);
      } else {
        response = await mockApi.signup(email.trim(), password);
      }

      if (response.success) {
        setSuccess(response.message);
        console.log('✅ Auth Success:', response.data);
        
        // Add a small delay so the user can see the green success message before navigating away
        setTimeout(() => {
          navigation.replace('Dashboard');
        }, 1000);
      } else {
        setError(response.message);
        console.log('❌ Auth Failed:', response.message);
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLoginMode(!isLoginMode);
    setError(null);
    setSuccess(null);
    setEmail('');
    setPassword('');
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <View style={styles.formContainer}>
        <Text style={styles.title}>
          {isLoginMode ? 'Welcome Back' : 'Create Account'}
        </Text>
        
        {error ? <Text style={styles.errorText}>{error}</Text> : null}
        {success ? <Text style={styles.successText}>{success}</Text> : null}

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Email</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter your email"
            placeholderTextColor="#999"
            value={email}
            onChangeText={(text) => {
              setEmail(text);
              if (error) setError(null);
              if (success) setSuccess(null);
            }}
            keyboardType="email-address"
            autoCapitalize="none"
            autoCorrect={false}
            editable={!loading}
          />
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Password</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter your password"
            placeholderTextColor="#999"
            value={password}
            onChangeText={(text) => {
              setPassword(text);
              if (error) setError(null);
              if (success) setSuccess(null);
            }}
            secureTextEntry
            autoCapitalize="none"
            editable={!loading}
          />
        </View>

        <TouchableOpacity 
          style={[styles.button, loading && styles.buttonDisabled]} 
          onPress={handleAuth}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>
              {isLoginMode ? 'Sign In' : 'Sign Up'}
            </Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.switchModeButton} 
          onPress={toggleMode}
          disabled={loading}
        >
          <Text style={styles.switchModeText}>
            {isLoginMode 
              ? "Don't have an account? Sign Up" 
              : "Already have an account? Sign In"}
          </Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  formContainer: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 32,
    textAlign: 'center',
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    fontWeight: '500',
  },
  input: {
    borderWidth: 1,
    borderColor: '#e1e1e1',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    backgroundColor: '#fafafa',
    color: '#333',
  },
  button: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 12,
  },
  buttonDisabled: {
    backgroundColor: '#99C7FF',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  switchModeButton: {
    marginTop: 24,
    alignItems: 'center',
    paddingVertical: 10,
  },
  switchModeText: {
    color: '#007AFF',
    fontSize: 15,
    fontWeight: '500',
  },
  errorText: {
    color: '#FF3B30',
    backgroundColor: '#FFE5E5',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    textAlign: 'center',
    overflow: 'hidden',
    fontWeight: '500',
  },
  successText: {
    color: '#34C759',
    backgroundColor: '#E5F9E7',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    textAlign: 'center',
    overflow: 'hidden',
    fontWeight: '500',
  },
});
