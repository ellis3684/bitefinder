# BiteFinder 🍴

A full-stack web app that helps users find meal combinations from nearby restaurants that fit within their calorie budget.

👉 **Live Demo:** [https://bitefinder.dev](https://bitefinder.dev)  
👉 **Backend API Docs:** [https://bitefinder.dev/api/docs/](https://bitefinder.dev/api/docs/)

---

## 🧑‍💻 About the Project

**BiteFinder** helps users answer the question:  
**"What can I eat nearby that fits my calorie limit?"**

Users enter a calorie target, browse nearby restaurants, and get meal recommendations from real menu items, pulled from external restaurant APIs.

The app combines:

- Location-based restaurant search (via **Foursquare Places API**)
- Menu item and calorie data (via **FatSecret API**)
- A local heuristic algorithm for calorie-based meal recommendation (no AI or ML)

---

## 🚀 Features

✅ Live demo deployed at [https://bitefinder.dev](https://bitefinder.dev)  
✅ Auto-generated **Backend API Docs** available at [https://bitefinder.dev/api/docs/](https://bitefinder.dev/api/docs/)  
✅ Search nearby restaurants by location  
✅ Browse real menu items with calorie info  
✅ Get meal suggestions that fit your calorie limit  
✅ Supports both chain and non-chain restaurants  
✅ REST API backend (Django + DRF)  
✅ React frontend (Vite + Tailwind CSS)  
✅ Fully Dockerized for development  
✅ Background tasks powered by Celery + Redis  

---

## 🛠️ Tech Stack

| Layer        | Tools                                 |
|--------------|---------------------------------------|
| Backend      | Django, Django REST Framework, Celery |
| Frontend     | React (Vite, Tailwind CSS)            |
| Database     | PostgreSQL                            |
| Caching/Queue| Redis                                  |
| APIs Used    | FatSecret API, Foursquare Places API |
| Containerization | Docker + Docker Compose           |

---

## ⚙️ Setup Instructions

### Prerequisites:
- Docker
- Docker Compose
- FatSecret API credentials
- Foursquare API credentials

---

### Development Setup:

```bash
# Clone the repo
git clone https://github.com/yourusername/bitefinder.git
cd bitefinder

# Build and run Docker containers
docker-compose up --build
