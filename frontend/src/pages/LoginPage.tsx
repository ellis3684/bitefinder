import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { Link, useNavigate } from "react-router-dom";
import Cookies from "js-cookie";
import { useUser } from "@/contexts/UserContext";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { fetchUser } = useUser();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Step 1: Get CSRF token
      await api.get("/users/csrf/");

      // Step 2: Login with CSRF header
      await api.post(
        "/users/login/",
        { username, password },
        {
          headers: {
            "X-CSRFToken": Cookies.get("csrftoken") || "",
          },
        }
      );

      // Step 3: Refresh user context and redirect
      await fetchUser();
      navigate("/");
    } catch (err) {
      console.error(err);
      setError("Invalid username or password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
        <Card className="w-full max-w-md p-8 space-y-6 shadow-lg">
          <h1 className="text-2xl font-semibold text-center mb-4">Login</h1>
          <form onSubmit={handleLogin} className="space-y-4">
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
              {loading ? "Logging in..." : "Sign In"}
            </Button>

            {error && (
              <p className="text-red-500 text-sm text-center">{error}</p>
            )}
          </form>

          <p className="text-center text-sm">
            Don’t have an account?{" "}
            <Link to="/signup" className="text-blue-500 hover:underline">
              Create one
            </Link>
          </p>
        </Card>
      </div>
    </>
  );
}
