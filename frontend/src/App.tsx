import { Routes, Route } from "react-router-dom";
import NavBar from "@/components/NavBar";
import HomePage from "@/pages/HomePage";
import LoginPage from "@/pages/LoginPage";
import RestaurantsPage from "@/pages/RestaurantsPage";
import RecommendMealPage from "@/pages/RecommendMealPage";
import SignupPage from "@/pages/SignupPage";
import MyMealsPage from "@/pages/MyMealsPage";
import NearbyRecommendPage from "@/pages/NearbyRecommendPage";
import BuildYourMealPage from "@/pages/BuildYourMealPage";

export default function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <NavBar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/menu-items/:id/" element={<BuildYourMealPage />} />
        <Route path="/recommend/nearby" element={<NearbyRecommendPage />} />
        <Route path="/restaurants/nearby" element={<RestaurantsPage type="nearby" />} />
        <Route path="/restaurants/all" element={<RestaurantsPage type="all" />} />
        <Route path="/restaurants/:id/recommend" element={<RecommendMealPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/users/me/meals" element={<MyMealsPage />} />
      </Routes>
    </div>
  );
}
