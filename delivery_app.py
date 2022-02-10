from app import create_app, db
from app.models import OrderFood, User, Address, MenuCategory, Food, Order

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Address': Address, 'MenuCategory': MenuCategory, 'Food': Food, 'Order': Order, 'OrderFood': OrderFood}
