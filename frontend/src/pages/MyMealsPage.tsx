import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Cookies from "js-cookie";

type MenuItem = {
  id: number;
  name: string;
  calories: number;
  restaurant: number;
};

type Restaurant = {
  id: number;
  name: string;
};

type UserMeal = {
  id: number;
  restaurant: Restaurant;
  menu_items: MenuItem[];
  created_at: string;
};

export default function MyMealsPage() {
  const [meals, setMeals] = useState<UserMeal[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchMeals = async () => {
      try {
        const res = await api.get("/users/me/meals/");
        setMeals(res.data);
      } catch (err) {
        console.error("Failed to fetch meals", err);
      } finally {
        setLoading(false);
      }
    };

    fetchMeals();
  }, []);

  const handleDelete = async (mealId: number) => {
    setDeletingId(mealId);
    try {
      await api.get("/users/csrf/");
      await api.delete(`/users/me/meals/${mealId}/`, {
        headers: {
          "X-CSRFToken": Cookies.get("csrftoken") || "",
        },
      });
      setMeals((prev) => prev.filter((meal) => meal.id !== mealId));
    } catch (err) {
      console.error("Failed to delete meal", err);
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return <p className="p-6 text-center">Loading saved meals...</p>;
  }

  return (
    <div className="p-6 space-y-6 w-full">
      <h1 className="text-2xl font-bold text-center">My Saved Meals</h1>

      {meals.length === 0 ? (
        <p className="text-center">You have no saved meals yet.</p>
      ) : (
        <div className="grid gap-6 grid-cols-[repeat(auto-fit,minmax(500px,1fr))]">
          {meals.map((meal) => {
            const totalCalories = meal.menu_items.reduce((sum, item) => sum + item.calories, 0);

            return (
              <Card key={meal.id} className="p-6 space-y-4 min-w-[500px]">
                <h2 className="text-lg font-semibold">{meal.restaurant.name}</h2>

                <div className="space-y-2">
                  {meal.menu_items.map((item) => (
                    <div key={item.id} className="flex justify-between text-sm">
                      <span>{item.name}</span>
                      <span>{item.calories} cal</span>
                    </div>
                  ))}
                </div>

                <p className="font-medium">Total: {totalCalories} cal</p>

                <Button
                  variant="destructive"
                  onClick={() => handleDelete(meal.id)}
                  disabled={deletingId === meal.id}
                >
                  {deletingId === meal.id ? "Deleting..." : "Delete This Meal"}
                </Button>
              </Card>
            );
          })}
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
