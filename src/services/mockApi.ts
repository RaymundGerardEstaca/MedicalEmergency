export const mockApi = {
  // Mock user database
  users: [
    {
      id: "1",
      email: "test@example.com",
      password: "password123",
      name: "Test User",
    },
  ],

  // Simulates network delay
  delay: (ms) => new Promise((resolve) => setTimeout(resolve, ms)),

  login: async function(email, password) {
    await this.delay(1500); // 1.5 second delay

    const user = this.users.find((u) => u.email === email);

    if (!user) {
      return {
        success: false,
        message: "User not found",
      };
    }

    if (user.password !== password) {
      return {
        success: false,
        message: "Incorrect password",
      };
    }

    // Exclude password from the returned user data
    const { password: _, ...userData } = user;

    return {
      success: true,
      message: "Login successful",
      data: {
        user: userData,
        token: `mock-jwt-token-${user.id}-${Date.now()}`,
      },
    };
  },

  signup: async function(email, password, name = "New User") {
    await this.delay(1500); // 1.5 second delay

    const existingUser = this.users.find((u) => u.email === email);

    if (existingUser) {
      return {
        success: false,
        message: "User already exists",
      };
    }

    const newUser = {
      id: Math.random().toString(36).substr(2, 9),
      email,
      password,
      name,
    };

    // Add to mock database
    this.users.push(newUser);

    const { password: _, ...userData } = newUser;

    return {
      success: true,
      message: "Signup successful",
      data: {
        user: userData,
        token: `mock-jwt-token-${newUser.id}-${Date.now()}`,
      },
    };
  },
};
