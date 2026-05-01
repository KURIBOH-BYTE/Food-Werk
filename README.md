# 🍔 FoodWerk – Fast Food Delivery & Pickup (Browser App)

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
- Customize items (remove ingredients, add extras, choose flavors)
- Manage a shopping cart
- Choose between delivery and pickup
- Pay securely with a card (test card simulation)
- Track their order status

Admins and employees can:
- Manage the menu (availability, new items)
- View and update all orders
- Create and manage special offers

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

### 6. Manage Orders (Admin)
**As an admin, I want to view all orders and update their status.**

- **Inputs:** order ID, new status
- **Outputs:** updated order

---

### 7. Manage Specials (Admin)
**As an admin, I want to create time-limited special offers for menu items.**

- **Inputs:** menu item, special price, start/end date, description
- **Outputs:** active special visible on the menu and specials page

---

## 🧩 Use Cases

### Main Use Cases
- Browse Menu (Customer)
- Add to Cart / Customize (Customer)
- Checkout & Pay (Customer)
- Track Order (Customer)
- Register / Login (Customer)
- Manage Menu (Admin/Employee)
- Manage Orders (Admin/Employee)
- Manage Specials (Admin)

### Actors
- Customer
- Employee
- Admin

---

## 🏛️ Architecture

### Layers
- **UI:** NiceGUI (browser-based interface)
- **Application logic:** Controllers and Services
- **Persistence:** SQLite + SQLModel ORM + Data Access (DAO)

### Design Decisions
- MVC structure (Model–View–Controller)
- Clear separation of concerns
- Business logic fully independent of the UI layer
- Server-side cart storage via NiceGUI's `app.storage.user`

### Design Patterns Used
- **Model-View-Controller / Layered MVC:** Separates UI, business logic, and database access for clarity, testability, and maintainability.
- **DAO Pattern (Data Access Object):** Each entity has its own DAO class that encapsulates all database queries.
- **Facade Pattern:** The `Database` class hides engine setup, schema creation, and seeding from the rest of the application.
- **Composition Root:** `FoodWerkApplication` wires all dependencies (DAOs, Services, Controllers, Pages) in one place.

---

## 🗄️ Database and ORM

The application uses **SQLModel** to map domain objects to a SQLite database.

<img width="1668" height="1597" alt="image" src="https://github.com/user-attachments/assets/c5fb7d40-3db5-4861-a6c1-3815f90bb24c" />


### Entities
- `User`
- `Category`
- `MenuItem`
- `Ingredient` / `MenuItemIngredient`
- `Extra`
- `Address`
- `Order` / `OrderItem` / `OrderItemExtra`
- `DeliveryInfo`
- `Special`
- `Review`

### Key Relationships
- One `User` → many `Order`, `Address`, `Review`
- One `Order` → many `OrderItem` → many `OrderItemExtra`
- One `Order` → one `DeliveryInfo`
- One `MenuItem` → many `Special`, `Review`, `MenuItemIngredient`

---

## ✅ Project Requirements

### 1. Browser-based App (NiceGUI)

The application runs entirely in the browser. Customers can browse the menu, manage their cart, checkout, and pay — all without page reloads. Admins manage orders and specials through a dedicated dashboard.

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

## 💳 Test Cards

The payment page uses simulated card validation — no real payment is processed.

| Card Number          | Brand      | Result          |
|----------------------|------------|-----------------|
| 4242 4242 4242 4242  | Visa       | Always succeeds |
| 5555 5555 5555 4444  | Mastercard | Always succeeds |
| 4000 0000 0000 0002  | Visa       | Always declined |

Use expiry `12/26` and CVV `123` for the success cards.

---

## ⚙️ Implementation

### Technology

- Python 3.9+
- NiceGUI
- SQLModel / SQLAlchemy
- bcrypt
- pytest

---

### Libraries Used

- **nicegui** – browser-based UI framework
- **sqlmodel** – ORM (SQLAlchemy + Pydantic combined)
- **sqlalchemy** – database toolkit
- **bcrypt** – password hashing
- **pytest** – testing

---

## 📂 Repository Structure

```text
FoodWerk/
├── requirements.txt
├── foodwerk/
│   ├── __main__.py
│   ├── application.py          ← Composition Root
│   ├── domain/
│   │   └── models.py           ← 13 SQLModel entities
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
│   │   ├── review_service.py
│   │   └── special_service.py
│   └── ui/
│       ├── controllers.py      ← Auth / Shopping / Admin / Payment
│       ├── pages.py            ← All NiceGUI routes
│       └── components.py       ← Reusable UI components
├── frontend/
│   └── static/                 ← Images, icons
└── tests/
    ├── conftest.py
    ├── test_auth_service.py
    ├── test_cart_service.py
    ├── test_menu_service.py
    ├── test_order_service.py
    ├── test_review_service.py
    └── test_special_service.py
```

---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/KURIBOH-BYTE/Food-Werk.git
cd foodwerk
```

### 2. Project Setup

- Python 3.13 is required
- Create and activate a virtual environment:

#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```
#### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```
- Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Launch
- Start the FoodWerk Website:

```bash
py -m foodwerk
``` 
- If the application does not open automatically, open the URL printed in the console (default: http://localhost:8080).

### 4. Demo Accounts

| Role     | Email               | Password      |
|----------|---------------------|---------------|
| Admin    | admin@foodwerk.ch   | admin123      |
| Employee | max@foodwerk.ch     | employee123   |

Register a new account to use the customer features.

### 5. Usage

**Order food:**
1. Go to **Menu** and browse by category.
2. Click an item to customize (remove ingredients, add notes).
3. Go to **Cart** and review your order.
4. Click **Checkout**, choose delivery or pickup, fill in details.
5. Enter a test card and click **Pay Now**.
6. Track your order on the confirmation page.

**Admin:**
1. Log in with `admin@foodwerk.ch` / `admin123`.
2. Navigate to **Admin** in the navbar.
3. Manage orders, menu availability, and specials.

---

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

**15 tests across 6 services:**

| File                     | Tests | What is tested                                      |
|--------------------------|-------|-----------------------------------------------------|
| `test_auth_service.py`   | 2     | User registration, login                            |
| `test_cart_service.py`   | 5     | Add, remove, update quantity, total, serialization  |
| `test_menu_service.py`   | 2     | Get categories, filter available items              |
| `test_order_service.py`  | 3     | Pickup order, delivery order, status update         |
| `test_special_service.py`| 2     | Create special, deactivate special                  |
| `test_review_service.py` | 1     | Create review                                       |

---

## 👥 Team & Contributions

| Name         | Contribution               |
|--------------|----------------------------|
| Roy Fluckiger | Database & ORM + documentation |
| Fabrice Balzan| NiceGUI UI + documentation     |
| Ryan Wolf     | Business logic + documentation |

---

## 📝 License

This project is provided for **educational use only** as part of the OOP module.
