# TNP Portal | Executive Dashboard

A comprehensive, full-stack Training and Placement (TNP) management platform designed for streamlined student and company coordination at IIIT Bhopal. Built with a modern tech stack to ensure a premium, minimal, and highly responsive administrative experience.

---

## 🏗️ Project Architecture

This repository is structured as a **Monorepo**, containing both the frontend and backend applications perfectly separated.

```text
TNP_FULLSTACK/
│
├── tnp_stuff/          # Backend (Python/Flask)
│   ├── app.py          # Main server entry point
│   ├── database/       # DB initialization scripts
│   ├── placements/     # API routes for placement data
│   ├── students/       # API routes for student data
│   └── requirements.txt# Python dependencies
│
└── PROJECT_STC/        # Frontend (React/Vite)
    ├── src/            # React components and pages
    ├── package.json    # Node dependencies
    └── vite.config.js  # Vite configuration

    🛠️ Tech Stack
Frontend: React.js, Vite, HTML/CSS (Modular Components)

Backend: Python, Flask, Flask-CORS

Database: MySQL, SQLAlchemy (ORM)

🚀 Getting Started
Follow these instructions to get a copy of the project up and running on your local machine for development and testing.

Prerequisites
Ensure you have the following installed on your system:

Python 3.9+

Node.js (v16+) & npm

MySQL Server

1. Database Setup
Before starting the backend, you must configure the local MySQL database. Open your MySQL command line or Workbench and execute:

SQL
CREATE DATABASE sonal_db;
CREATE USER 'krishnagupta'@'localhost' IDENTIFIED BY 'godkrishna';
GRANT ALL PRIVILEGES ON sonal_db.* TO 'krishnagupta'@'localhost';
FLUSH PRIVILEGES;
2. Backend Setup (tnp_stuff)
The backend serves the REST API and manages database connections.

Navigate to the backend directory:

Bash
cd tnp_stuff
Create a virtual environment:

Bash
python -m venv tnp_env
Activate the virtual environment:

Windows: tnp_env\Scripts\activate

Mac/Linux: source tnp_env/bin/activate

Install the required dependencies:

Bash
pip install -r requirements.txt
Initialize the database (Run this only once to build tables):

Bash
python database/build.py
Start the server:

Bash
python app.py
The API will be live at http://127.0.0.1:5000

3. Frontend Setup (PROJECT_STC)
The frontend is a Vite-powered React dashboard. Open a new terminal window (leave the backend running) and follow these steps:

Navigate to the frontend directory:

Bash
cd PROJECT_STC
Install Node modules:

Bash
npm install
Start the development server:

Bash
npm run dev
The dashboard will be accessible at http://localhost:5173