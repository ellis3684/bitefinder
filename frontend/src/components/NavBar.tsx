import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import Cookies from "js-cookie";
import { api } from "@/lib/api";
import { useUser } from "@/contexts/UserContext";

export default function NavBar() {
  const navigate = useNavigate();
  const { user, setUser } = useUser();

  const handleLogout = async () => {
    try {
      await api.get("/users/csrf/");
      await api.post(
        "/users/logout/",
        {},
        {
          headers: {
            "X-CSRFToken": Cookies.get("csrftoken") || "",
          },
        }
      );
      setUser(null);
      navigate("/");
    } catch (err) {
      console.error("Logout failed", err);
    }
  };

  return (
    <nav className="flex items-center justify-between px-6 py-4 border-b border-gray-200 shadow-sm">
      <div
        className="font-bold text-3xl flex items-center cursor-pointer"
        onClick={() => navigate("/")}
      >
        <img src="/logo.png" alt="BiteFinder Logo" className="w-10 h-10 mr-3" />
        BiteFinder
      </div>

      {user ? (
        <div className="flex gap-4 items-center">
          <Button variant="ghost" onClick={() => navigate("/users/me/meals")}>
            My Meals
          </Button>
          <Button size="lg" className="px-6 py-3 text-base" onClick={handleLogout}>
            Logout
          </Button>
        </div>
      ) : (
        <Button
          size="lg"
          className="px-6 py-3 text-base"
          onClick={() => navigate("/login")}
        >
          Login
        </Button>
      )}
    </nav>
  );
}
