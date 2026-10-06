# StockPilot - Inventory Management System

A full-stack web application to manage product inventory. Users can add, search, update stock and delete product records, with automatic low-stock alerts, all without page reloads.

## Features

* Add, view, edit and delete products (ID, Name, Category, Quantity, Price)
* Live search by product name, ID or category, plus category filter
* Increase or decrease stock with +/- buttons
* Low-stock alerts (quantity of 10 or less) and out-of-stock badges
* Dashboard cards: total products, total units, inventory value, low-stock count
* Input validation: no negative quantity or price, stock cannot go below zero
* Dynamic updates using the Fetch API (no page reload)

## Technologies Used

|Layer|Tools|
|-|-|
|Frontend|HTML5, CSS3, JavaScript (Fetch API)|
|Tooling|Node.js, npm, live-server|
|Backend|Python, Flask, Flask-CORS (REST API)|
|Database|SQLite|
|Editor|Visual Studio Code|

## Project Structure

```
Inventory-System/
├── Backend/
│   ├── app.py              # Flask REST API + serves the frontend
│   ├── requirements.txt    # Python dependencies
│   ├── package.json        # Node.js tooling
│   ├── inventory.db        # SQLite database (auto-created)
│   └── frontend/
│       ├── index.html
│       ├── style.css
│       └── script.js
└── README.md
```

## API Endpoints

|Method|Endpoint|Purpose|
|-|-|-|
|GET|`/api/products?q=\&category=`|List / search products|
|POST|`/api/products`|Add a product|
|PUT|`/api/products/<id>`|Update product details|
|PATCH|`/api/products/<id>/stock`|Change stock by +/- amount|
|DELETE|`/api/products/<id>`|Delete a product|
|GET|`/api/stats`|Dashboard statistics|
|GET|`/api/categories`|List categories|

## Prerequisites

* [Python 3.10+](https://www.python.org/downloads/)
* [Node.js (LTS)](https://nodejs.org/) (optional, for frontend tooling)
* [Git](https://git-scm.com/)

## How to Run

1. Clone the repository

```
   git clone https://github.com/24mishram1-wq/Inventory-System.git
   cd Inventory-System/Backend
   ```

2. (Recommended) Create and activate a virtual environment

```
   python -m venv venv
   venv\\Scripts\\activate        # Windows
   source venv/bin/activate     # Mac/Linux
   ```

3. Install Python dependencies

```
   pip install -r requirements.txt
   ```

4. Start the server

```
   python app.py
   ```

5. Open your browser at **http://127.0.0.1:5000**

The SQLite database and `products` table are created automatically on first run.

### Optional: Node.js frontend tooling

```
npm install
npm run dev
```

This starts a live-reload server on port 5500. If you use it, set `const API = "http://127.0.0.1:5000/api";` in `frontend/script.js`.

## Edge Cases Tested

* Searching for a product that does not exist shows "No products found"
* Reducing stock below zero is rejected with an error message
* Negative price or quantity is rejected (frontend and backend)
* Empty name or category is rejected
* Server offline shows a clear error message

## Author

Name - Mahek Mishra 
Roll. No - 37
Branch - ECE

