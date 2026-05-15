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
- **Outputs:** active special visible on the menu and specials page

---

### 8. Manage Specials (Admin)
**As an admin, I want to create time-limited special offers for menu items.**

- **Inputs:** menu item, special price, start/end date, description
- **Outputs:** active special visible on the menu and specials page

---

## 🧩 Use Cases
<img width="862" height="510" alt="image" src="https://github.com/user-attachments/assets/950faebd-7fe4-40ee-b999-d42891b6a1b8" />


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
### Wireframe Wireframes / Mockups
<img width="1319" height="879" alt="image" src="https://github.com/user-attachments/assets/db188b1d-c988-410e-bda9-c552d4d0d9f1" />

<img width="555" height="894" alt="image" src="https://github.com/user-attachments/assets/d8f10c6d-cd10-43a9-a337-7e522199dce5" />


## 🏛️ Architecture

<img width="1119" height="1600" alt="image" src="https://github.com/user-attachments/assets/b7a6e527-e5f6-4e4b-be4a-4e0af1508549" />

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
# Klassendiagramm
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/6257f1c3-4bb7-45b1-882c-4dd788c48bb1" />

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
- **CartService** — In-memory shopping cart with automatic 10% discount from CHF 50
- **CartItem** — Individual item in the shopping cart
- **PaymentService** — Stripe Checkout integration

## Controller Layer (UI-Koordination)

The controllers mediate between the UI layer (NiceGUI Pages) and the services.

- **AuthController** — Login, registration, session management
- **ShoppingController** — Menu, shopping cart, order processing
- **AdminController** — Order management, menu management, specials
- **PaymentController** — Stripe Checkout flow
## 🗄️ Database and ORM

The application uses **SQLModel** to map domain objects to a SQLite database.

<img width="1756" height="1993" alt="ERM drawio" src="https://github.com/user-attachments/assets/d07f8499-6357-4872-9642-9528451b02df" />

### Entities
- User
- Category
- MenuItem
- Ingredient / MenuItemIngredient
- DeliveryAddress
- Order / OrderItem
  
### Key Relationships
- One Order → one DeliveryAddress (optional, bei Lieferung)
- One User → many DeliveryAddress
- One User → many MenuItem (created_by)
- One MenuItem → many MenuItemIngredient

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
.venv\Scripts\activate
```

**Step 5 – Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 6 – Run the application**
```bash
python3 -m foodwerk
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

<img width="1882" height="488" alt="Screenshot 2026-05-15 123602" src="https://github.com/user-attachments/assets/367b1764-4ca0-4193-b348-153b0fa01c3c" />
<img width="732" height="586" alt="Screenshot 2026-05-15 121739" src="https://github.com/user-attachments/assets/a4db94d2-57ee-4432-b998-2a20bcc45072" />
<img width="1112" height="340" alt="Screenshot 2026-05-15 122400" src="https://github.com/user-attachments/assets/aa76ccae-d045-49d3-b9ee-6ca64a87252b" />


**Admin:**
1. Log in with `admin@foodwerk.ch` / `admin123`.
2. Navigate to **Admin** in the navbar.
3. Manage orders, menu availability, and specials.

<img width="1270" height="329" alt="Screenshot 2026-05-15 123743" src="https://github.com/user-attachments/assets/f643a7b7-9d86-4f06-a391-c34822a612f6" />
<img width="1727" height="761" alt="Screenshot 2026-05-15 123844" src="https://github.com/user-attachments/assets/c497f626-f207-4ce2-944e-b775b3407307" />



---
# Testing

Die Tests sind in drei Schichten aufgeteilt und befinden sich im Ordner `tests/`.

## Ausführen

```bash
# Alle Tests
pytest

# Einzelne Datei
pytest tests/test_unit.py
pytest tests/test_db.py
pytest tests/test_integration.py

# Mit Output
pytest -v
```

## Teststruktur

### `test_unit.py` — Unit Tests

Testet die Geschäftslogik von `CartService` isoliert, ohne Datenbank.

| Test | Beschreibung |
|---|---|
| `test_subtotal_empty_cart` | Leerer Warenkorb hat Subtotal 0.0 |
| `test_subtotal_single_item` | Subtotal wird korrekt berechnet |
| `test_discount_applied_above_50` | 10% Rabatt wird ab CHF 50.01 angewendet |
| `test_no_discount_exactly_50` | Kein Rabatt bei genau CHF 50.00 |
| `test_no_discount_below_50` | Kein Rabatt unter CHF 50.00 |
| `test_total_reflects_discount` | Total = Subtotal - Rabatt |

### `test_db.py` — Datenbank Tests

Testet DAOs direkt mit einer In-Memory SQLite Datenbank (kein externes Setup nötig).

| Test | Beschreibung |
|---|---|
| `test_menu_query_returns_seeded_items` | Verfügbare Menüartikel werden korrekt abgefragt |
| `test_unavailable_items_excluded_from_available_query` | Nicht verfügbare Artikel werden gefiltert |
| `test_saving_order_persists_order_and_items` | Bestellung und Bestellpositionen werden gespeichert |

### `test_integration.py` — Integrationstests

Testet den vollständigen Checkout-Ablauf mit `MenuService`, `CartService` und `OrderService` zusammen.

| Test | Beschreibung |
|---|---|
| `test_checkout_single_item_creates_order` | Bestellung mit einem Artikel wird erstellt |
| `test_checkout_multiple_items_applies_discount` | Rabatt wird bei Subtotal > CHF 50 angewendet |
| `test_checkout_exactly_50_no_discount` | Kein Rabatt bei exakt CHF 50.00 |

## Technologie

- **pytest** — Test-Framework
- **SQLModel** — ORM für Modelle und Queries
- **SQLite In-Memory** (`sqlite:///:memory:`) — temporäre Datenbank pro Test, kein externes Setup erforderlich

## Rabattlogik

Der `CartService` berechnet automatisch einen Mengenrabatt:

```
Subtotal > CHF 50.00  →  10% Rabatt
Subtotal ≤ CHF 50.00  →  kein Rabatt
```


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
