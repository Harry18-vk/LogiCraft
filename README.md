# LogiCraft — Logistics & Fleet Management System
**Project Code:** P_012 | **Domain:** Transportation & Supply Chain Telematics

LogiCraft is a centralized logistics, fleet tracking, warehouse inventory, and public-transport scheduling & ticketing web application built using **Python**, **Django**, and **MySQL**.

---

## 🛠️ Technology Stack
- **Backend:** Python 3.13, Django 6.1
- **Database:** MySQL 8.0 (with dual-mode SQLite support via `.env`)
- **Driver / Connector:** PyMySQL (`pymysql.install_as_MySQLdb()`) & Cryptography
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons
- **Visual Analytics:** Chart.js
- **Environment Management:** `python-dotenv`

---

## 📦 Architecture & App Modules

| Django App | Key Features & Responsibilities |
| :--- | :--- |
| **`users`** | Role-Based Access Control (`ADMIN`, `LOGISTICS_MANAGER`, `DRIVER`, `CUSTOMER`), Custom User Model. |
| **`fleet`** | Vehicle registration, payload capacity, powertrain types, certified drivers, and maintenance logs. |
| **`warehouse`** | Storage hubs, regional sorting facilities, SKU items, unit weight, and stock alert levels. |
| **`shipments`** | Freight booking, vehicle & driver assignment, live milestone checkpoints, and **public tracking**. |
| **`transport`** | Intercity bus routes, terminals, distances, timetables, and tariffs. |
| **`bookings`** | Passenger seat reservation, fare calculation, and electronic boarding pass issuance. |
| **`dashboard`** | Centralized analytics, KPI cards, vehicle telematics distribution, and recent operations. |

---

## 🚀 Quick Start Guide

### 1. Activate the Virtual Environment
Open PowerShell inside `C:\Users\divya\logicraft`:
```powershell
cd C:\Users\divya\logicraft
.\venv\Scripts\Activate.ps1
```

### 2. Configure Database (.env)
The project includes dual-mode database configuration in `.env`:
```env
# Switch to MySQL 8.0
USE_SQLITE=False
DB_NAME=logicraft_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

# Or toggle USE_SQLITE=True for lightweight zero-config testing
USE_SQLITE=True
```

### 3. Apply Database Migrations
```powershell
python manage.py migrate
```

### 4. Seed Prototype Demo Data
Populates realistic vehicles, warehouses, shipments, routes, and user accounts:
```powershell
python manage.py seed_data
```

### 5. Run the Development Server
```powershell
python manage.py runserver
```
Visit: **http://127.0.0.1:8000/**

---

## 🔑 Pre-configured Demo Accounts

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `admin123` | Full access + Django Admin (`/admin/`) |
| **Logistics Manager** | `manager1` | `manager123` | Operations dashboard, fleet, warehouse, shipments |
| **Fleet Driver** | `driver_rajesh` | `driver123` | Assigned vehicle, delivery status updates |

---

## 🗺️ Key Application Endpoints

- **Operations Dashboard:** `http://127.0.0.1:8000/`
- **Fleet & Drivers:** `http://127.0.0.1:8000/fleet/`
- **Register Vehicle:** `http://127.0.0.1:8000/fleet/vehicle/add/`
- **Consignments & Shipments:** `http://127.0.0.1:8000/shipments/`
- **Public Package Tracking (No Login Required):** `http://127.0.0.1:8000/shipments/track/`
- **Warehouses & Inventories:** `http://127.0.0.1:8000/warehouse/`
- **Bus Routes & Schedules:** `http://127.0.0.1:8000/transport/`
- **Passenger Bookings & Tickets:** `http://127.0.0.1:8000/bookings/`
- **Django Admin Site:** `http://127.0.0.1:8000/admin/`

---

## 🧪 Running Automated Tests
```powershell
python manage.py test dashboard
```
