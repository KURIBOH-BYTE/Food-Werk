# 🍔 FoodWerk – Fast Food Delivery & Pickup (Browser App)
<img width="1875" height="966" alt="image" src="https://github.com/user-attachments/assets/3201e041-e9b6-4050-8675-95693297d180" />

---

This project demonstrates the development of a browser-based ordering application using **NiceGUI**, focusing on clean architecture, data validation, and database integration via an ORM.

It aims to:

- Cover the full process from **requirements analysis to implementation**
- Apply advanced **Python** concepts in a web-based application
- Demonstrate **data validation**, layered architecture, and ORM usage
- Produce clean, maintainable, and well-tested code

---

## 📝 Application Requirements

### Problem

Fast food restaurants often rely on manual order taking, which leads to errors, missing customizations, and slow processing.

---

### Scenario

The application allows customers to:
- Browse a menu with categories (Burgers, Pizza, Sides, Drinks, Desserts)
- Customize items (remove ingredients)
- Manage a shopping cart
- Choose between delivery and pickup
- Pay securely with a card (test card simulation)
- Track their order status

Admins can:
- Create and manage special offers
- Manage the menu (availability, new items)
- View and update all orders
  
employees can:
- Manage the menu (availability, new items)
- View and update all orders


---

## 📖 User Stories

### 1. Browse the Menu
**As a customer, I want to see all menu items grouped by category.**

- **Inputs:** none
- **Outputs:** list of categories and items with prices and images

---

### 2. Customize and Add to Cart
**As a customer, I want to customize an item and add it to my cart.**

- **Inputs:** item ID, removed ingredients, extras, notes
- **Outputs:** updated cart with total

---

### 3. Checkout
**As a customer, I want to choose delivery or pickup and enter my details.**

- **Inputs:** order type, delivery address or pickup time, notes
- **Outputs:** saved order intent, redirect to payment

---

### 4. Pay by Card
**As a customer, I want to enter my card details and complete the payment.**

- **Inputs:** card number, expiry, CVV, name
- **Outputs:** payment confirmation, order created, order ID

---

### 5. Track Order Status
**As a customer, I want to see the current status of my order.**

- **Inputs:** order ID
- **Outputs:** status (pending → preparing → ready → delivered/collected)

---

### 6. Manage Orders (Admin/Employee)
**As an admin or employee, I want to view all orders and update their status.**

- **Inputs:** order ID, new status
- **Outputs:** updated order

---

### 7. Manage Menu (Admin/Employee)
**As an admin or employee, I want to manage the availability of items to keep the menu up to date.**

- **Inputs:** availability status (in stock/out of stock).
- **Outputs:** updated item availability reflected in the menu

---

### 8. Manage Specials (Admin)
**As an admin, I want to create time-limited special offers for menu items.**

- **Inputs:** menu item, special price, start/end date, description
- **Outputs:** active special visible on the menu and specials page

---

### 9. Download Receipt (Customer)
**As a customer, I want to download a PDF receipt for my completed order.**

- **Inputs:** order ID
- **Outputs:** PDF receipt with order details, items, and total

---

## 🧩 Use Cases
<img width="862" height="510" alt="image" src="https://github.com/user-attachments/assets/950faebd-7fe4-40ee-b999-d42891b6a1b8" />


### Main Use Cases
- Browse Menu (Customer)
- Add to Cart / Customize (Customer)
- Checkout & Pay (Customer)
- Track Order (Customer)
- Download PDF Receipt (Customer)
- Register / Login (Customer)
- Manage Menu (Admin/Employee)
- Manage Orders (Admin/Employee)
- Manage Specials (Admin)

### Actors
- Customer
- Employee
- Admin

---
## 🌄 Wireframe Wireframes / Mockups
<img width="1319" height="879" alt="image" src="https://github.com/user-attachments/assets/db188b1d-c988-410e-bda9-c552d4d0d9f1" />

<img width="555" height="894" alt="image" src="https://github.com/user-attachments/assets/d8f10c6d-cd10-43a9-a337-7e522199dce5" />

---

## 🏛️ Architecture

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/75f5dbb7-ada8-45bc-bdc4-d50b4c34742a" />



### Design Patterns Used
- **Model-View-Controller / Layered MVC:** Separates UI, business logic, and database access for clarity, testability, and maintainability.
- **DAO Pattern (Data Access Object):** Each entity has its own DAO class that encapsulates all database queries.
- **Facade Pattern:** The `Database` class hides engine setup, schema creation, and seeding from the rest of the application.
- **Composition Root:** `FoodWerkApplication` wires all dependencies (DAOs, Services, Controllers, Pages) in one place.

---
## 📈 Class Diagram
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/49b6e5f0-63eb-47a5-98cc-57759fb0f546" />


The class diagram shows the complete architecture of FoodWerk divided into four layers.

## Domain Model (Entities)

The database classes are based on SQLModel and are stored directly in the SQLite database. The following entities are present:

- User — User with role (admin, employee, customer)
- DeliveryAddress — Delivery addresses of a user
- Category — Menu categories (e.g. Burgers, Pizza)
- Ingredient — Ingredients
- MenuItem — Menu items with price, availability, and discount
- MenuItemIngredient — Junction table between MenuItem and Ingredient
- Order — A user's order
- OrderItem — Individual line item within an order

## DAO Layer (Data Access Layer)

The DAO classes (Data Access Objects) are responsible for database access. All DAOs inherit from `BaseDAO` and use SQLModel sessions.

- **UserDAO** — CRUD operations for users
- **DeliveryAddressDAO** — Management of delivery addresses
- **CategoryDAO** — Querying of categories
- **MenuItemDAO** — Management of menu items including availability, specials, and discounts
- **OrderDAO** — Creating and querying orders

## Service Layer (Business Logic)

The services contain the business logic. They use the DAOs for data access and inherit from `BaseService`.

- **AuthService** — Registration, login, password management, delivery addresses
- **MenuService** — Menu management, specials, discounts
- **OrderService** — Order creation and status management
- **CartService** — In-memory shopping cart (total always equals subtotal)
- **CartItem** — Individual item in the shopping cart
- **PaymentService** — Stripe Checkout integration
- **ReceiptService** — PDF receipt generation for completed orders

## Controller Layer (UI Coordination)

The controllers mediate between the UI layer (NiceGUI Pages) and the services.

- **AuthController** — Login, registration, session management
- **ShoppingController** — Menu, shopping cart, order processing
- **AdminController** — Order management, menu management, specials
- **PaymentController** — Stripe Checkout flow
  
---

## 🗄️ Database and ORM

The application uses **SQLModel** to map domain objects to a SQLite database.

<img width="1756" height="1993" alt="ERM drawio" src="https://github.com/user-attachments/assets/d07f8499-6357-4872-9642-9528451b02df" />

### Entities
- User
- Category
- MenuItem
- Ingredient
- MenuItemIngredient
- DeliveryAddress
- Order
- OrderItem

### Key Relationships
- One **User** → many **Order**
- One **User** → many **DeliveryAddress**
- One **User** → many **MenuItem** *(created_by)*
- One **Order** → one **DeliveryAddress** *(optional, only for delivery)*
- One **Order** → many **OrderItem**
- One **MenuItem** → many **OrderItem**
- One **MenuItem** → many **MenuItemIngredient**
- One **Ingredient** → many **MenuItemIngredient**
- One **Category** → many **MenuItem**

---

## ✅ Project Requirements

### 1. Browser-based App (NiceGUI)

Customers can browse the menu, manage their cart, checkout, and pay — all without page reloads. 
Admins manage orders and specials through a dedicated dashboard.

**Architecture note:** The browser is a thin client; all UI state and business logic live on the server-side NiceGUI app.

---

### 2. Data Validation

All user input is validated before being processed:

- **Registration:** email uniqueness, password confirmation
- **Checkout:** required address fields for delivery orders
- **Card payment:** card number format (13–19 digits), MM/YY expiry format, 3–4 digit CVV, name required, test card recognition
- **Specials:** end date must be after start date, price must be positive
- **Order status:** only valid transitions are accepted

---

### 3. Database Management

All data is managed via **SQLModel** (built on SQLAlchemy). The database is automatically created and seeded with demo data on first startup.

---

## ⚙️ Implementation

### Technology

- Python 3.9+
- NiceGUI
- SQLModel / SQLAlchemy
- bcrypt
- pytest


### Libraries Used

- **nicegui** – browser-based UI framework
- **sqlmodel** – ORM (SQLAlchemy + Pydantic combined)
- **sqlalchemy** – database toolkit
- **bcrypt** – password hashing
- **pytest** – testing
- **fpdf2** – PDF generation for receipts
- **stripe** – payment integration

---

## 📂 Repository Structure

```text
FoodWerk/
├── requirements.txt
├── .env.example
├── .gitignore
├── start.sh
├── foodwerk/
│   ├── __main__.py
│   ├── application.py          ← Composition Root
│   ├── domain/
│   │   └── models.py           ← 8 SQLModel entities
│   ├── data_access/
│   │   ├── dao.py              ← DAOs per entity
│   │   ├── db.py               ← Database facade
│   │   └── seed.py             ← Demo data seeder
│   ├── services/
│   │   ├── base_service.py
│   │   ├── auth_service.py
│   │   ├── cart_service.py
│   │   ├── menu_service.py
│   │   ├── order_service.py
│   │   ├── payment_service.py
│   │   └── receipt_service.py
│   └── ui/
│       ├── controllers.py      ← Auth / Shopping / Admin / Payment
│       ├── pages.py            ← All NiceGUI routes
│       └── components.py       ← Reusable UI components
├── data/                       ← SQLite database (created on first run)
├── frontend/
│   └── static/
│       └── images/             ← Product images & logo
└── tests/
    ├── conftest.py
    ├── test_db.py              ← DAO database tests
    ├── test_integration.py     ← End-to-end checkout tests
    ├── test_auth_service.py
    ├── test_cart_service.py
    ├── test_menu_service.py
    └── test_order_service.py
```

---

## 🚀 How to Run

## Requirements
- Python 3.9+
  
**Step 1 – Clone the repository**
```bash
git clone https://github.com/KURIBOH-BYTE/Food-Werk.git
```

**Step 2 – Navigate into the project folder**
```bash
cd Food-Werk
```

**Step 3 – Create a virtual environment**
```bash
python -m venv .venv --without-pip
```

**Step 4 – Activate the virtual environment**
```bash
.venv/Scripts/activate
```

**Step 5 – Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 6 – Run the application**
```bash
python -m foodwerk
```
- If the application does not open automatically, open the URL printed in the console (default: http://localhost:8080).

---

## 👷 How to Use

### Demo Accounts

| Role     | Email               | Password    |
|----------|---------------------|-------------|
| Admin    | admin@foodwerk.ch   | admin123    |
| Employee | max@foodwerk.ch     | employee123 |

> [!NOTE]
> To explore the customer-facing features, register a new account.



### 🛒 Ordering Food

1. Go to **Menu** and browse items by category
2. Click any item to customize it (e.g. remove ingredients)
3. Open **Cart** to review your order
4. Click **Checkout**, select delivery or pickup, and fill in your details
5. Enter a test card number and click **Pay Now**
6. Track your order status on the confirmation page
7. Visit **My Account** to view your order history and download a PDF receipt for any past order

<img width="1882" alt="Menu overview" src="https://github.com/user-attachments/assets/367b1764-4ca0-4193-b348-153b0fa01c3c" />
<img width="732" alt="Item customization" src="https://github.com/user-attachments/assets/a4db94d2-57ee-4432-b998-2a20bcc45072" />
<img width="1112" alt="Checkout flow" src="https://github.com/user-attachments/assets/aa76ccae-d045-49d3-b9ee-6ca64a87252b" />

### 🔧 Admin Panel

1. Log in with `admin@foodwerk.ch` / `admin123`
2. Click **Admin** in the navigation bar
3. Manage orders, control menu item availability, and configure daily specials

<img width="1270" alt="Admin navbar" src="https://github.com/user-attachments/assets/f643a7b7-9d86-4f06-a391-c34822a612f6" />
<img width="1727" alt="Admin panel" src="https://github.com/user-attachments/assets/c497f626-f207-4ce2-944e-b775b3407307" />


### 💳 Test Cards

> [!IMPORTANT]
> The payment page uses simulated card validation — no real payment is ever processed.

| Card Number           | Brand      | Result          |
|-----------------------|------------|-----------------|
| `4242 4242 4242 4242` | Visa       | ✅ Always succeeds |
| `5555 5555 5555 4444` | Mastercard | ✅ Always succeeds |
| `4000 0000 0000 0002` | Visa       | ❌ Always declined |

Use expiry `12/26` and CVV `123` with the success cards.

---

## ⚠️ Testing

Tests are split across six files and live in the `tests/` folder. The suite covers the most critical paths: authentication, cart logic, database persistence, menu queries, order management, and the full checkout flow — **15 tests** in total.

## Running

```bash
# All tests
pytest

# Single file
pytest tests/test_auth_service.py
pytest tests/test_cart_service.py
pytest tests/test_db.py
pytest tests/test_integration.py
pytest tests/test_menu_service.py
pytest tests/test_order_service.py

# With verbose output
pytest -v
```

## Test Structure

### `test_auth_service.py` — AuthService Tests

Tests the core registration and login flow.

| Test | Description |
|---|---|
| `test_register_creates_user` | New user is saved correctly |
| `test_login_success` | Login with correct credentials returns user |
| `test_login_wrong_password` | Login with wrong password returns None |

### `test_cart_service.py` — CartService Tests

Tests cart operations without a database.

| Test | Description |
|---|---|
| `test_add_item` | Item is added to the cart |
| `test_remove_item` | Item is removed and cart becomes empty |
| `test_total` | Total is calculated correctly for multiple items |

### `test_db.py` — Database Tests

Tests DAOs directly with an in-memory SQLite database (no external setup required).

| Test | Description |
|---|---|
| `test_menu_query_returns_seeded_items` | Available menu items are queried correctly |
| `test_saving_order_persists_order_and_items` | Order and order items are persisted correctly |

### `test_integration.py` — Integration Tests

Tests the full checkout flow with `MenuService`, `CartService`, and `OrderService` together.

| Test | Description |
|---|---|
| `test_checkout_single_item_creates_order` | Order with a single item is created correctly |
| `test_checkout_multiple_items_total_equals_subtotal` | Total equals subtotal for multi-item orders |
| `test_checkout_total_matches_cart` | Order total always matches the cart total exactly |

### `test_menu_service.py` — MenuService Tests

Tests menu queries and category filtering.

| Test | Description |
|---|---|
| `test_get_menu_items_available_only` | Only available items are returned |
| `test_get_menu_items_by_category` | Filtering by category works correctly |

### `test_order_service.py` — OrderService Tests

Tests order creation and status transitions.

| Test | Description |
|---|---|
| `test_create_pickup_order` | Pickup order is created and cart is cleared |
| `test_update_order_status` | Order status is updated correctly |

## Technology

- **pytest** — testing framework
- **SQLModel** — ORM for models and queries
- **SQLite In-Memory** (`sqlite:///:memory:`) — temporary database per test, no external setup required


---

## 👥 Team & Contributions

| Name         | Contribution               |
|--------------|----------------------------|
| Roy Flückiger | Database & ORM + documentation |
| Fabrice Balzan| NiceGUI UI + documentation     |
| Ryan Wolf     | Business logic + documentation |

---

## 📝 License

This project is provided for **educational use only** as part of the OOP module.
