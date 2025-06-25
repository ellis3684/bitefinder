import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import Cookies from "js-cookie";

type MealItem = {
  id: number;
  name: string;
  calories: number;
  restaurant_name: string;
};

type MealCombination = {
  items: MealItem[];
  restaurant_name: string;
  restaurant_id: number;
};

type Restaurant = {
  id: number;
  name: string;
};

export default function NearbyRecommendPage() {
  const navigate = useNavigate();
  const [calorieLimit, setCalorieLimit] = useState("");
  const [recommendations, setRecommendations] = useState<MealCombination[]>([]);
  const [loading, setLoading] = useState(false);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [savingIndex, setSavingIndex] = useState<number | null>(null);
  const [savedIndices, setSavedIndices] = useState<number[]>([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const checkLogin = async () => {
      try {
        await api.get("/users/me/");
        setIsLoggedIn(true);
      } catch {
        setIsLoggedIn(false);
      }
    };
    checkLogin();
  }, []);

  const shuffleArray = <T,>(array: T[]): T[] => {
    return array
      .map((value) => ({ value, sort: Math.random() }))
      .sort((a, b) => a.sort - b.sort)
      .map(({ value }) => value);
  };

  const handleFetchRecommendations = () => {
    if (!navigator.geolocation) {
      setLocationError("Geolocation is not supported by your browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        setLocationError(null);
        setLoading(true);
        try {
          const nearbyRes = await api.get("/restaurants/nearby/", {
            params: {
              lat: position.coords.latitude,
              lng: position.coords.longitude,
            },
          });

          const nearbyRestaurants: Restaurant[] = nearbyRes.data;

          const recResponses = await Promise.all(
            nearbyRestaurants.map(async (restaurant) => {
              try {
                const recRes = await api.get(
                  `/menu-items/recommend/${restaurant.id}/${calorieLimit}/`
                );

                const mealsFromThisRestaurant: MealCombination[] =
                  shuffleArray(recRes.data.recommended_meals)
                    .slice(0, 5)
                    .map((combo: any) => ({
                      items: combo.items.map((item: any) => ({
                        ...item,
                        restaurant_name: restaurant.name,
                      })),
                      restaurant_name: restaurant.name,
                      restaurant_id: restaurant.id,
                    }));

                return mealsFromThisRestaurant;
              } catch (err) {
                console.warn(`No recommendations for ${restaurant.name} (ID ${restaurant.id})`);
                return [];
              }
            })
          );

          const allMeals: MealCombination[] = recResponses.flat();
          setRecommendations(allMeals);
          setSavedIndices([]);
        } catch (err) {
          console.error("Failed to fetch meal recommendations", err);
        } finally {
          setLoading(false);
        }
      },
      (error) => {
        console.error("Location error", error);
        setLocationError("Failed to get location. Please enable location services.");
      }
    );
  };

  const handleSaveMeal = async (comboIndex: number) => {
    const combo = recommendations[comboIndex];
    const menuItemIds = combo.items.map((item) => item.id);

    setSavingIndex(comboIndex);
    try {
      await api.get("/users/csrf/");

      await api.post(
        "/users/me/meals/",
        {
          restaurant_id: combo.restaurant_id,
          menu_item_ids: menuItemIds,
        },
        {
          headers: {
            "X-CSRFToken": Cookies.get("csrftoken") || "",
          },
        }
      );

      setSavedIndices((prev) => [...prev, comboIndex]);
    } catch (err) {
      console.error("Failed to save meal", err);
    } finally {
      setSavingIndex(null);
    }
  };

  const groupedByRestaurant: { [restaurantName: string]: MealCombination[] } = {};
  recommendations.forEach((combo) => {
    if (!groupedByRestaurant[combo.restaurant_name]) {
      groupedByRestaurant[combo.restaurant_name] = [];
    }
    groupedByRestaurant[combo.restaurant_name].push(combo);
  });

  return (
    <div className="p-6 space-y-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-center">Nearby Meal Recommendations</h1>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleFetchRecommendations();
        }}
        className="flex flex-col sm:flex-row gap-4"
      >
        <Input
          type="number"
          placeholder="Enter calorie limit"
          value={calorieLimit}
          onChange={(e) => setCalorieLimit(e.target.value)}
        />
        <Button type="submit" disabled={loading || !calorieLimit}>
          {loading ? "Loading..." : "Find Meals Near Me"}
        </Button>
      </form>

      {locationError && <p className="text-red-500">{locationError}</p>}

      {Object.keys(groupedByRestaurant).length > 0 && (
        <div className="space-y-8">
          {Object.entries(groupedByRestaurant).map(([restaurantName, combos]) => (
            <div key={restaurantName} className="space-y-4">
              <h2 className="text-xl font-bold">{restaurantName}</h2>

              {combos.map((combo, _index) => {
                const globalIndex = recommendations.indexOf(combo);
                const totalCalories = combo.items.reduce(
                  (sum, item) => sum + item.calories,
                  0
                );

                return (
                  <Card key={globalIndex} className="p-4 space-y-2">
                    <h3 className="font-semibold">Meal Option</h3>
                    {combo.items.map((item) => (
                      <div key={item.id} className="flex justify-between text-sm">
                        <span>{item.name}</span>
                        <span>{item.calories} cal</span>
                      </div>
                    ))}
                    <p className="font-medium">Total: {totalCalories} cal</p>

                    {isLoggedIn && (
                      <Button
                        onClick={() => handleSaveMeal(globalIndex)}
                        disabled={savingIndex === globalIndex || savedIndices.includes(globalIndex)}
                      >
                        {savingIndex === globalIndex
                          ? "Saving..."
                          : savedIndices.includes(globalIndex)
                          ? "Saved"
                          : "Save This Meal"}
                      </Button>
                    )}
                  </Card>
                );
              })}
            </div>
          ))}
        </div>
      )}

      <div className="text-center">
        <Button variant="secondary" onClick={() => navigate("/")}>
          Back to Home
        </Button>
      </div>
    </div>
  );
}
