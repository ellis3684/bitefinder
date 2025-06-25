import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import Cookies from "js-cookie";
import { Heart } from "lucide-react";

type Restaurant = {
  id: number;
  name: string;
  formatted_address?: string;
};

export default function RestaurantsPage({ type }: { type: "nearby" | "all" }) {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [favoriteIds, setFavoriteIds] = useState<number[]>([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const fetched = useRef(false);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchData() {
      try {
        // Check if user is logged in
        setIsLoggedIn(true);

        // If logged in, fetch favorites
        const favRes = await api.get("/users/me/favorites/");
        const favIds = favRes.data.favorite_restaurants.map((r: any) => r.id);
        setFavoriteIds(favIds);

        await fetchRestaurants(favIds);
      } catch (err: any) {
        const status = err.response?.status;
        if (status === 401 || status === 403) {
          // Not logged in
          setIsLoggedIn(false);
          await fetchRestaurants([]); // Load restaurants with no favorites
        } else {
          setError("Could not fetch restaurants.");
          console.error(err);
        }
      }
    }

    const fetchRestaurants = async (favIds: number[]) => {
      try {
        if (type === "nearby") {
          navigator.geolocation.getCurrentPosition(async (pos) => {
            const res = await api.get("/restaurants/nearby/", {
              params: {
                lat: pos.coords.latitude,
                lng: pos.coords.longitude,
              },
            });
            sortAndSetRestaurants(res.data, favIds);
          });
        } else {
          const res = await api.get("/restaurants/supported/");
          sortAndSetRestaurants(res.data, favIds);
        }
      } catch (err) {
        setError("Could not fetch restaurants.");
        console.error(err);
      }
    };

    if (!fetched.current) {
      fetched.current = true;
      fetchData();
    }
  }, [type]);

  const sortAndSetRestaurants = (restaurantList: Restaurant[], favIds: number[]) => {
    const sorted = [...restaurantList].sort((a, b) => {
      const aFav = favIds.includes(a.id);
      const bFav = favIds.includes(b.id);
      if (aFav && !bFav) return -1;
      if (!aFav && bFav) return 1;
      return 0;
    });
    setRestaurants(sorted);
  };

  const toggleFavorite = async (restaurantId: number, isCurrentlyFavorite: boolean) => {
    try {
      await api.get("/users/csrf/");

      if (isCurrentlyFavorite) {
        await api.delete("/users/me/favorites/", {
          data: { restaurant_id: restaurantId },
          headers: { "X-CSRFToken": Cookies.get("csrftoken") || "" },
        });
        setFavoriteIds((prev) => prev.filter((id) => id !== restaurantId));
      } else {
        await api.post(
          "/users/me/favorites/",
          { restaurant_id: restaurantId },
          {
            headers: { "X-CSRFToken": Cookies.get("csrftoken") || "" },
          }
        );
        setFavoriteIds((prev) => [...prev, restaurantId]);
      }
    } catch (err) {
      console.error("Error updating favorite", err);
    }
  };

  const normalize = (text: string) => text.toLowerCase().replace(/[^a-z0-9]/g, "");
  const filteredRestaurants = restaurants.filter((r) =>
    normalize(r.name).includes(normalize(search))
  );

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">
        {type === "nearby" ? "Nearby Restaurants" : "All Supported Restaurants"}
      </h1>

      <Input
        type="text"
        placeholder="Search restaurants..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="max-w-sm"
      />

      {error && <p className="text-red-500">{error}</p>}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredRestaurants.map((r) => {
          const isFavorite = favoriteIds.includes(r.id);
          return (
            <Card
              key={r.id}
              onClick={() => navigate(`/restaurants/${r.id}/recommend`)}
              className="p-4 space-y-2 cursor-pointer hover:bg-gray-50 transition"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">{r.name}</h2>

                {isLoggedIn && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleFavorite(r.id, isFavorite);
                    }}
                    className={`ml-2 ${
                      isFavorite ? "text-red-500" : "text-gray-400 hover:text-red-500"
                    }`}
                  >
                    <Heart fill={isFavorite ? "currentColor" : "none"} />
                  </button>
                )}
              </div>

              {r.formatted_address && (
                <p className="text-sm text-muted-foreground">{r.formatted_address}</p>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}
