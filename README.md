# 🎬 CineVerse - Movie Ticket Booking System

A full-stack web application for booking movie tickets with user management and analytics.

## Features
- **User Management** - Create, edit, delete users
- **Ticket Booking** - Browse movies, select shows, book tickets
- **Analytics Dashboard** - 10 SQL queries for insights
- **Booking Management** - View and cancel bookings

## Tech Stack
- **Backend:** Python, Flask, MySQL
- **Frontend:** HTML, Tailwind CSS, JavaScript
- **Database:** MySQL with Stored Procedures & Triggers

## Installation

```bash
# Clone repository
git clone https://github.com/gourishmoger3-design/movie_booking.git
cd movie_booking

# Install dependencies
pip install flask flask-cors mysql-connector-python
Access at: http://localhost:5000

Database Setup
Create MySQL database CineBookingDB

Run the SQL script to create tables and sample data

Update password in app.py

Project Structure
├── app.py              # Flask backend
├── templates/
│   └── index.html      # Frontend UI
└── database.sql        # Database schema
Author
Gourish Moger | GitHub

Repository
https://github.com/gourishmoger3-design/movie_booking

**Copy this entire block and paste into your `README.md` file.**

Then run:
```bash
git add README.md
git commit -m "Add README"
git push


# Update database password in app.py
# Run the application
python app.py
