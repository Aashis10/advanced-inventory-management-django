# Aashish Tech Suppliers - Inventory Management System

Aashish Tech Suppliers is a production-ready inventory management web application built with Django and MySQL. It is designed for small and medium electronics suppliers to manage products, sales, purchases, stock movement, staff activity, analytics, and report exports from a single dashboard.

## Core Highlights
- Modern SaaS-style dashboard UI with light and dark mode
- Real dynamic analytics using Chart.js
- Inventory control with low stock alerts and reorder suggestions
- Sales and purchase tracking with paid amount and balance due
- Category and product management with image support
- Activity log for staff operations
- CSV and PDF report exports

## Tech Stack
- Backend: Django
- Database: MySQL (SQLite fallback for local testing)
- Frontend: Bootstrap 5, HTML, CSS, JavaScript
- Visualization: Chart.js
- Reporting: ReportLab (PDF)

## Functional Modules
1. Dashboard
- KPI cards for products, inventory value, daily sales, low stock, categories
- Monthly sales trend, category revenue distribution, top selling products

2. Inventory
- Product CRUD with filters (search, category, brand, stock)
- Stock status badges (In Stock, Low Stock, Out of Stock)
- Product detail page with supplier and sales history

3. Categories
- Icon-based category cards
- Product count and description
- Click-through category details

4. Sales
- Buyer name, payment method, quantity, amount paid, balance due
- Automatic stock deduction
- Receipt preview

5. Purchases
- Supplier, payment tracking, purchase date, paid/balance values
- Automatic stock increase

6. Analytics
- Revenue, profit margin, sales by category, stock movement, stock snapshot

7. Reports
- Sales, Purchase, Inventory, Low Stock, and Profit reports
- Export to CSV and PDF

## Demo Data System
The project includes a permanent demo data mechanism so dashboards and reports are never empty during deployment demos.

- Management command: `python manage.py seed_demo_data`
- Auto-seed: runs on startup when product table exists and has zero records
- Generates realistic products, categories, suppliers, purchases, and sales

## Local Setup
1. Create and activate virtual environment
2. Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. Run migrations:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

4. (Optional) Seed demo data manually:

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo_data
```

5. Run the server:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

## Production Notes
- Use environment variables for DB credentials and secret key
- Set `DEBUG=False` and configure `ALLOWED_HOSTS`
- Run `collectstatic` before deployment
- Auto demo seeding can be disabled using `AUTO_SEED_DEMO_DATA=0`

## Demo Credentials
- Admin: `admin` / `admin12345`
- Staff: `staff` / `staff12345`
- [![Deploy to Render](https://render.com/badge.svg)](https://advanced-inventory-management-django.onrender.com/)
