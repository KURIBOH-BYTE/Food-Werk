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


def test_saving_order_persists_order_and_items(seeded_engine):
    with Session(seeded_engine) as session:
        menu_item = session.exec(select(MenuItem).where(MenuItem.name == "Classic Burger")).first()

    from foodwerk.data_access.dao import UserDAO
    user_dao = UserDAO(seeded_engine)
    users = user_dao.get_all()
    user_id = users[0].id

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
