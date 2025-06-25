import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { useNavigate } from "react-router-dom";
import { useUser } from "@/contexts/UserContext";

export default function SignupPage() {
  const { user, fetchUser } = useUser();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      navigate("/");
    }
  }, [user, navigate]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Step 1: Create the account
      await api.post("/users/create/", { username, password });

      // Step 2: Immediately log in
      await api.post("/users/login/", { username, password });

      // Step 3: Refresh user context
      await fetchUser();

      // Step 4: Redirect to homepage
      navigate("/");
    } catch (err) {
      console.error(err);
      alert("Signup or login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <Card className="w-full max-w-md p-8 space-y-6 shadow-lg">
        <h1 className="text-2xl font-semibold text-center">Create Account</h1>
        <form onSubmit={handleRegister} className="space-y-4">
          <Input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Creating account..." : "Sign Up"}
          </Button>
        </form>
      </Card>
    </div>
  );
}
