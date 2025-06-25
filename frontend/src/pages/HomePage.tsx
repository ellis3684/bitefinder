import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="flex-grow flex items-center justify-center px-6 py-12 text-center">
      <div className="flex flex-col items-center gap-10 w-full max-w-4xl">
        <h1 className="text-6xl font-bold text-primary mb-4">Welcome to BiteFinder</h1>

        <p className="text-lg text-muted-foreground max-w-lg mb-12 leading-relaxed">
          Find meal recommendations from nearby restaurants that fit your calorie limit.
        </p>

        <div className="flex flex-col sm:flex-row gap-6 w-full justify-center">
          <Button
            size="lg"
            className="w-full sm:w-auto px-8 py-5 text-lg"
            onClick={() => navigate("/recommend/nearby")}
          >
            Find Meals Near Me
          </Button>

          <Button
            variant="secondary"
            size="lg"
            className="w-full sm:w-auto px-8 py-5 text-lg"
            onClick={() => navigate("/restaurants/nearby")}
          >
            Nearby Restaurants
          </Button>

          <Button
            variant="secondary"
            size="lg"
            className="w-full sm:w-auto px-8 py-5 text-lg"
            onClick={() => navigate("/restaurants/all")}
          >
            All Restaurants
          </Button>
        </div>
      </div>
    </div>
  );
}
