import React, { createContext, useContext, useState, useCallback } from "react";
import api from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem("cc_user");
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const login = useCallback(async (email, password) => {
    const res = await api.post("/api/auth/login", { email, password });
    const data = res.data;
    localStorage.setItem("cc_token", data.access_token);
    localStorage.setItem("cc_user", JSON.stringify({
      user_id: data.user_id,
      name: data.name,
      email: data.email,
    }));
    setUser({ user_id: data.user_id, name: data.name, email: data.email });
    return data;
  }, []);

  const register = useCallback(async (name, email, password, confirm_password) => {
    const res = await api.post("/api/auth/register", {
      name,
      email,
      password,
      confirm_password,
    });
    const data = res.data;
    localStorage.setItem("cc_token", data.access_token);
    localStorage.setItem("cc_user", JSON.stringify({
      user_id: data.user_id,
      name: data.name,
      email: data.email,
    }));
    setUser({ user_id: data.user_id, name: data.name, email: data.email });
    return data;
  }, []);

  const updateName = useCallback(async (name) => {
    const res = await api.put("/api/auth/me", { name });
    const nextUser = { ...user, ...res.data };
    localStorage.setItem("cc_user", JSON.stringify(nextUser));
    setUser(nextUser);
    return nextUser;
  }, [user]);

  const logout = useCallback(() => {
    localStorage.removeItem("cc_token");
    localStorage.removeItem("cc_user");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, register, updateName, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
