"""Database tests — query and persistence via DAOs with in-memory SQLite."""

from sqlmodel import Session, select

from foodwerk.domain.models import MenuItem, Order, OrderItem
from foodwerk.data_access.dao import MenuItemDAO, OrderDAO


def test_menu_query_returns_seeded_items(seeded_engine):
    with Session(seeded_engine) as session:
        items = session.exec(select(MenuItem).where(MenuItem.is_available == True)).all()

    assert len(items) == 3
    names = {i.name for i in items}
    assert "Classic Burger" in names
    assert "Cheeseburger" in names
    assert "Cola" in names


def test_unavailable_items_excluded_from_available_query(seeded_engine):
    dao = MenuItemDAO(seeded_engine)
    available = dao.get_all(available_only=True)
    all_items = dao.get_all(available_only=False)

    assert len(all_items) == 4
    assert len(available) == 3
    assert all(i.is_available for i in available)


def test_saving_order_persists_order_and_items(seeded_engine):
    with Session(seeded_engine) as session:
        menu_item = session.exec(select(MenuItem).where(MenuItem.name == "Classic Burger")).first()
        user_id = menu_item.category_id  # just need any valid FK — use real user_id below

    # Get a real user_id from the seeded DB
    from foodwerk.data_access.dao import UserDAO
    user_dao = UserDAO(seeded_engine)
    users = user_dao.get_all()
    user_id = users[0].id

    order_dao = OrderDAO(seeded_engine)
    order = Order(
        user_id=user_id,
        order_type="pickup",
        total_price=12.90,
        status="pending",
    )
    with Session(seeded_engine) as session:
        session.add(order)
        session.commit()
        session.refresh(order)

        item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=1,
            unit_price=12.90,
        )
        session.add(item)
        session.commit()

        stored_items = session.exec(
            select(OrderItem).where(OrderItem.order_id == order.id)
        ).all()

    assert len(stored_items) == 1
    assert stored_items[0].unit_price == 12.90
