from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from marshmallow import fields, validate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:amrit101!@localhost/e_commerce_api'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'use_pure': True}
}
db = SQLAlchemy(app)
ma = Marshmallow(app)

class UserSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ('name','email','phone','id')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class AccountSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

    class Meta:
        fields = ('username','password','user_id')

account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)

class ProductSchema(ma.Schema):
    name = fields.String(required=True)
    price = fields.Float(required=True)
    quantity = fields.Integer(required=True)

    class Meta:
        fields = ('name','price','quantity','id')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

class OrderSchema(ma.Schema):
    date = fields.String(required=True)
    user_id = fields.Integer(required=True)
    total_price = fields.Float(required=True, validate=validate.Range(min=0))

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


order_product = db.Table('order_product',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref='user')

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    orders = db.relationship('Order', secondary=order_product, backref=db.backref('order_items', lazy='dynamic'))

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_price = db.Column(db.Float, nullable=False)
    order_products = db.relationship('Product', secondary=order_product, backref=db.backref('products', lazy='dynamic'))

class CustomerAccount(db.Model):
    __tablename__ = 'customer_accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='customer_accounts', uselist=False)


@app.route('/')
def home():
    return "Welcome to the E Commerce API Database!"

@app.route('/users', methods=['GET'])
def read_users():
    users = User.query.all()
    return users_schema.jsonify(users)

@app.route('/user', methods=['POST'])
def create_users():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_user = User(name=user_data['name'], email=user_data['email'], phone=user_data['phone'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"Attn": "New user added successfully"}), 201

@app.route('/users/<int:id>', methods=['PUT'])
def update_users(id):
    user = User.query.get_or_404(id)
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user.name = user_data['name']
    user.email = user_data['email']
    user.phone = user_data['phone']

    db.session.commit()
    return jsonify({"Attn": "Customer details updated successfully"}), 200

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_users(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"Attn": "User has been deleted successfully"}), 200

@app.route('/accounts', methods=['POST'])
def create_user_accounts():
    try:
        account_data = account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_user_account = CustomerAccount(username=account_data['username'], password=account_data['password'], user_id=account_data['user_id'])
    db.session.add(new_user_account)
    db.session.commit()
    return jsonify({"Attn": "New user account added successfully"}), 201

@app.route('/accounts', methods=['GET'])
def read_user_accounts():
    user_accounts = CustomerAccount.query.all()
    return accounts_schema.jsonify(user_accounts)

@app.route('/accounts/<int:user_id>', methods=['PUT'])
def update_user_accounts(user_id):
    user_account = CustomerAccount.query.get_or_404(user_id)
    try:
        account_data = account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user_account.user_name = account_data['username']
    user_account.password = account_data['password']

    db.session.commit()
    return jsonify({"Attn": "Customer's account details updated successfully"}), 200

@app.route('/accounts/<int:user_id>', methods=['DELETE'])
def delete_user_accounts(user_id):
    user_account = CustomerAccount.query.get_or_404(user_id)
    db.session.delete(user_account)
    db.session.commit()
    return jsonify({"Attn": "User account has been deleted successfully"}), 200

@app.route('/products', methods=['POST'])
def create_products():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'], quantity=product_data['quantity'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"Attn": "New product has been added successfully"}), 201

@app.route('/products/<int:id>', methods=['GET'])
def read_product(id):
    product_info = Product.query.get_or_404(id)
    return product_schema.jsonify(product_info)

@app.route('/products/<int:id>', methods=['PUT'])
def update_products(id):
    products = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    products.name = product_data['name']
    products.price = product_data['price']
    products.quantity = product_data['quantity']

    db.session.commit()
    return jsonify({"Attn": "Product details updated successfully"}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_products(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"Attn": "Product has been deleted successfully"}), 200

@app.route('/stock/<int:id>', methods=['GET'])
def view_and_manage_stock(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    product.quantity = product_data['quantity']
    db.session.commit()
    return jsonify({"Attn": "Product quantity details have beeen updated successfully"}), 200

@app.route('/orders', methods=['POST'])
def order_products():
    try:
        order_data = order_schema.load(request.json)
        products = Product.query.all()
        total_price = 0
        for item in products:
            product = Product.query.get(item['product_id'])
            total_price += product.price * item['quantity']
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_order = Order(date=order_data['date'], user_id=order_data['user_id'], total_price=total_price)
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"Attn": "New order has been created successfully"})

@app.route('/orders/<int:id>', methods=['GET'])
def retrieve_orders(id):
    order = Order.query.get_or_404(id)
    return order_schema.jsonify(order)

@app.route('/orders/<int:id>', methods=['DELETE'])
def cancel_order(id):
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"Attn": "This order has been canceled successfully"}), 200
    

with app.app_context():
    db.create_all()

if __name__ == '__main__':
        app.run(debug=True)
