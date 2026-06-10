# 🅿️ Vehicle Parking App

A full-stack web application that allows users to search, reserve, and manage parking spaces in real time. Administrators get a dedicated dashboard to manage parking facilities, track spot occupancy, handle user accounts, and evaluate revenue trends through dynamic charts.

---

## Features

### User side
- **Search & discover** — find available parking lots by name, address, or pin code
- **Reserve a spot** — book an available spot instantly with vehicle number
- **Release & billing** — release a spot and get auto-calculated cost based on hours parked
- **Booking history** — view active and past reservations from a personal dashboard
- **Usage summary** — visual chart showing your occupied spots vs others across all lots

### Admin side
- **Facility management** — add, edit, and delete parking lots with configurable spot counts and pricing
- **Live occupancy tracking** — monitor available and occupied spots across all facilities
- **User management** — view all registered users
- **Revenue & analytics** — stacked bar chart (available vs occupied) and pie chart showing revenue contribution by parking lot

---

## Tech Stack

| Layer    | Technology                             |
|----------|----------------------------------------|
| Backend  | Python, Flask                          |
| Database | SQLite (via Flask-SQLAlchemy)          |
| Auth     | Flask sessions, Werkzeug password hashing |
| Charts   | Matplotlib (server-side rendered)      |
| Frontend | HTML, CSS, Jinja2 templates            |

---

## Data Models

| Model         | Description                                           |
|---------------|-------------------------------------------------------|
| `User`        | Registered users including the admin account          |
| `Parking`     | Parking lots with location, price, and spot count     |
| `ParkingSpot` | Individual spots within a lot (Available / Occupied)  |
| `Booking`     | Reservation records linking users, spots, and billing |

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Install dependencies
pip install flask flask-sqlalchemy werkzeug matplotlib

# Run the app
python app.py
```

The app will be available at `http://localhost:5000`

### Default admin credentials

```
Username: admin
Password: app123
```

---

## Project Structure

```
vehicle-parking-app/
├── app.py                  # Main application — routes, models, logic
├── parking.db              # SQLite database (auto-created on first run)
├── static/
│   └── charts/             # Generated chart images (bar & pie)
└── templates/
    ├── index.html
    ├── login.html
    ├── signup.html
    ├── admin.html
    ├── user.html
    ├── parking.html
    ├── add_parking.html
    ├── edit_parking.html
    ├── booking.html
    ├── booking_history.html
    ├── summary.html
    ├── user_summary.html
    ├── manage_user.html
    └── logout.html
```

---

## Academic Note

Originally developed as part of the **IIT Madras — Modern Application Development 1 (MAD 1)** course.  
Forked and maintained here for portfolio purposes and continued development.
