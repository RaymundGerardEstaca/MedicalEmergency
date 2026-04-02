import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import Login from './src/components/Login';
import SignUp from './src/components/SignUp';
import Dashboard from './src/components/Dashboard';
import DiscoverCameras from './src/components/DiscoverCameras';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login" screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Login" component={Login} />
        <Stack.Screen name="SignUp" component={SignUp} />
        <Stack.Screen name="Dashboard" component={Dashboard} />
        <Stack.Screen name="DiscoverCameras" component={DiscoverCameras} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
