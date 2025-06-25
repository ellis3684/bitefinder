import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { api } from "@/lib/api";
import Cookies from "js-cookie";
import { useUser } from "@/contexts/UserContext";

type MenuItem = {
  id: number;
  name: string;
  calories: number;
};

export default function BuildYourMealPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useUser();

  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    const fetchMenuItems = async () => {
      try {
        const res = await api.get(`/menu-items/restaurant/${id}/`);
        setMenuItems(res.data);
      } catch (err) {
        console.error("Failed to fetch menu items", err);
      } finally {
        setLoading(false);
      }
    };

    fetchMenuItems();
  }, [id]);

  const toggleItem = (itemId: number) => {
    setSelectedIds((prev) =>
      prev.includes(itemId) ? prev.filter((id) => id !== itemId) : [...prev, itemId]
    );
  };

  const handleSaveMeal = async () => {
    if (!id || selectedIds.length === 0) return;

    setSaving(true);
    try {
      await api.get("/users/csrf/");
      await api.post(
        "/users/me/meals/",
        {
          restaurant_id: parseInt(id),
          menu_item_ids: selectedIds,
        },
        {
          headers: {
            "X-CSRFToken": Cookies.get("csrftoken") || "",
          },
        }
      );
      setSaveSuccess(true);
    } catch (err) {
      console.error("Failed to save meal", err);
      alert("Failed to save meal.");
    } finally {
      setSaving(false);
    }
  };

  const totalCalories = menuItems
    .filter((item) => selectedIds.includes(item.id))
    .reduce((sum, item) => sum + item.calories, 0);

  if (loading) {
    return <p className="p-6 text-center">Loading menu items...</p>;
  }

  return (
    <div className="p-6 space-y-6 w-full">
      <h1 className="text-2xl font-bold text-center">Build Your Own Meal</h1>

      <div className="relative">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_220px] gap-6">
          {/* Left: Menu Items */}
          <div className="grid gap-6 grid-cols-[repeat(auto-fit,minmax(300px,1fr))]">
            {menuItems.map((item) => {
              const selected = selectedIds.includes(item.id);
              return (
                <Card
                  key={item.id}
                  onClick={() => toggleItem(item.id)}
                  className={`p-4 space-y-2 cursor-pointer border-2 ${
                    selected ? "border-blue-500" : "border-gray-200"
                  }`}
                >
                  <div className="flex justify-between">
                    <span>{item.name}</span>
                    <span>{item.calories} cal</span>
                  </div>
                  {selected && (
                    <p className="text-sm text-blue-500 font-medium">Selected</p>
                  )}
                </Card>
              );
            })}
          </div>

          {/* Right: Cart */}
          <div className="w-full lg:w-64 space-y-4 sticky top-6 self-start border border-gray-200 p-4 rounded">
            <h2 className="text-lg font-semibold">Your Meal</h2>

            {selectedIds.length === 0 ? (
              <p className="text-gray-500 text-sm">No items selected yet.</p>
            ) : (
              <ul className="space-y-1 text-sm">
                {menuItems
                  .filter((item) => selectedIds.includes(item.id))
                  .map((item) => (
                    <li key={item.id} className="flex justify-between">
                      <span>{item.name}</span>
                      <span>{item.calories} cal</span>
                    </li>
                  ))}
              </ul>
            )}

            <p className="font-medium">Total: {totalCalories} cal</p>

            {user ? (
              <Button
                size="lg"
                className="w-full"
                onClick={handleSaveMeal}
                disabled={saving || selectedIds.length === 0 || saveSuccess}
              >
                {saving ? "Saving..." : "Save This Meal"}
              </Button>
            ) : (
              <p className="text-gray-500 text-sm">Log in to save your meal.</p>
            )}

            <Button variant="secondary" className="w-full" onClick={() => navigate("/")}>
              Back to Home
            </Button>
          </div>
        </div>

        {saveSuccess && (
          <div className="fixed top-16 bottom-0 left-0 right-0 bg-white bg-opacity-80 flex items-center justify-center z-50">
            <div className="flex flex-col items-center space-y-4">
              <p className="text-green-600 font-semibold text-lg">Meal saved!</p>
              <Button
                onClick={() => {
                  setSelectedIds([]);
                  setSaveSuccess(false);
                }}
              >
                Build Another Meal
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
