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
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/db0fbf8e-4d20-44f2-b236-5d1f87b66676" />

Das Klassendiagramm zeigt die vollständige Architektur von FoodWerk aufgeteilt in vier Schichten.

## Domain Model (Entities)

Die Datenbankklassen basieren auf SQLModel und werden direkt in die SQLite-Datenbank gespeichert. Folgende Entities sind vorhanden:

- **User** — Benutzer mit Rolle (admin, employee, customer)
- **DeliveryAddress** — Lieferadressen eines Benutzers
- **Category** — Menükategorien (z.B. Burgers, Pizza)
- **Ingredient** — Zutaten
- **MenuItem** — Menüartikel mit Preis, Verfügbarkeit und Rabatt
- **MenuItemIngredient** — Verbindungstabelle zwischen MenuItem und Ingredient
- **Order** — Bestellung eines Benutzers
- **OrderItem** — Einzelne Position innerhalb einer Bestellung

## DAO Layer (Data Access Layer)

Die DAO-Klassen (Data Access Objects) sind für den Datenbankzugriff zuständig. Alle DAOs erben von `BaseDAO` und verwenden SQLModel-Sessions.

- **UserDAO** — CRUD-Operationen für Benutzer
- **DeliveryAddressDAO** — Verwaltung von Lieferadressen
- **CategoryDAO** — Abfrage von Kategorien
- **MenuItemDAO** — Verwaltung von Menüartikeln inkl. Verfügbarkeit, Specials und Rabatte
- **OrderDAO** — Erstellen und Abfragen von Bestellungen

## Service Layer (Business Logic)

Die Services enthalten die Geschäftslogik. Sie nutzen die DAOs für den Datenzugriff und erben von `BaseService`.

- **AuthService** — Registrierung, Login, Passwortverwaltung, Lieferadressen
- **MenuService** — Menüverwaltung, Specials, Rabatte
- **OrderService** — Bestellerstellung und Statusverwaltung
- **CartService** — In-Memory Warenkorb mit automatischem 10% Rabatt ab CHF 50
- **CartItem** — Einzelne Position im Warenkorb
- **PaymentService** — Stripe Checkout Integration

## Controller Layer (UI-Koordination)

Die Controller vermitteln zwischen der UI-Schicht (NiceGUI Pages) und den Services.

- **AuthController** — Login, Registrierung, Session-Verwaltung
- **ShoppingController** — Menü, Warenkorb, Bestellabwicklung
- **AdminController** — Bestellverwaltung, Menüverwaltung, Specials
- **PaymentController** — Stripe Checkout Flow
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

**Admin:**
1. Log in with `admin@foodwerk.ch` / `admin123`.
2. Navigate to **Admin** in the navbar.
3. Manage orders, menu availability, and specials.

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
