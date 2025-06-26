import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { api } from "@/lib/api";
import Cookies from "js-cookie";
import { useUser } from "@/contexts/UserContext";

type MealItem = {
  id: number;
  name: string;
  calories: number;
};

type MealCombination = {
  items: MealItem[];
};

export default function RecommendMealPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [calories, setCalories] = useState("");
  const [recommendations, setRecommendations] = useState<MealCombination[]>([]);
  const [loading, setLoading] = useState(false);
  const [savingIndex, setSavingIndex] = useState<number | null>(null);
  const [savedIndices, setSavedIndices] = useState<number[]>([]);
  const [noResults, setNoResults] = useState(false);
  const { user } = useUser();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setNoResults(false);
    try {
      const res = await api.get(`/menu-items/recommend/${id}/${calories}/`);
      setRecommendations(res.data.recommended_meals);
      setSavedIndices([]);
      setNoResults(res.data.recommended_meals.length === 0);
    } catch (err) {
      console.error("Failed to fetch recommendation", err);
      setNoResults(true);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveMeal = async (comboIndex: number) => {
    if (!id) return;
    const combo = recommendations[comboIndex];
    const menuItemIds = combo.items.map((item) => item.id);

    setSavingIndex(comboIndex);
    try {
      await api.get("/users/csrf/");

      await api.post(
        "/users/me/meals/",
        {
          restaurant_id: parseInt(id),
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

  return (
    <>
      <div className="p-6 space-y-6 w-full">
        <h1 className="text-2xl font-bold text-center">Meal Recommendation</h1>

        <div className="max-w-xl mx-auto w-full">
          <form onSubmit={handleSubmit} className="flex gap-4 w-full">
            <Input
              type="number"
              placeholder="Calorie limit"
              value={calories}
              onChange={(e) => setCalories(e.target.value)}
              required
              className="flex-grow"
            />
            <Button
              type="submit"
              size="lg"
              className="px-6 py-3 text-base"
              disabled={loading}
            >
              {loading ? "Loading..." : "Recommend"}
            </Button>
          </form>

          <div className="flex items-center gap-2 my-4">
            <hr className="flex-grow border-gray-300" />
            <span className="text-gray-500 text-sm">or</span>
            <hr className="flex-grow border-gray-300" />
          </div>

          <div className="text-center">
            <Button
              variant="outline"
              onClick={() => navigate(`/menu-items/${id}/`)}
            >
              Build Your Own Meal
            </Button>
          </div>
        </div>

        {recommendations.length > 0 && (
          <div className="grid gap-6 grid-cols-[repeat(auto-fit,minmax(500px,1fr))]">
            {recommendations.map((combo, index) => {
              const totalCalories = combo.items.reduce((sum, item) => sum + item.calories, 0);

              return (
                <Card key={index} className="p-6 space-y-4 min-w-[500px]">
                  <h2 className="text-lg font-semibold">Meal Option {index + 1}</h2>

                  <div className="space-y-2">
                    {combo.items.map((item) => (
                      <div key={item.id} className="flex justify-between text-sm">
                        <span>{item.name}</span>
                        <span>{item.calories} cal</span>
                      </div>
                    ))}
                  </div>

                  <p className="font-medium">Total: {totalCalories} cal</p>
                  {user && (
                    <Button
                      size="lg"
                      className="px-6 py-3 text-base"
                      onClick={() => handleSaveMeal(index)}
                      disabled={savingIndex === index || savedIndices.includes(index)}
                    >
                      {savingIndex === index
                        ? "Saving..."
                        : savedIndices.includes(index)
                        ? "Saved"
                        : "Save This Meal"}
                    </Button>                  
                  )}
                </Card>
              );
            })}
          </div>
        )}

        {!loading && recommendations.length === 0 && noResults && (
          <div className="text-center text-gray-500 mt-4">
            No meal combinations found for this calorie limit.
          </div>
        )}

        <div className="text-center">
          <Button variant="secondary" onClick={() => navigate("/")}>
            Back to Home
          </Button>
        </div>
      </div>
    </>
  );
}
