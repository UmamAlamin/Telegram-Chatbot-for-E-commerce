from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from typing import List
# Import the Pydantic models from models.py
from models import Product, Order, OrderTracking, User, Cart, ProductOrder, OrderTrackingItem

app = FastAPI()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["telebot"]


# Product CRUD
class ProductInput(BaseModel):
    id_produk: str = ""
    nama_produk: str
    harga_produk: float
    stok: int
    berapa_kilo: float

@app.post("/products/", response_model=Product)
def create_product(product: ProductInput):
    product_data = product.dict()
    result = db.products.insert_one(product_data)
    product.id_produk = str(result.inserted_id)
    return product

@app.get("/products/", response_model=List[Product])
def read_products(skip: int = 0, limit: int = 100):
    products = []
    for product_data in db.products.find().skip(skip).limit(limit):
        product = Product(**product_data)
        product.id_produk = str(product_data["_id"])
        products.append(product)
    return products

@app.get("/products/{product_id}", response_model=Product)
def read_product(product_id: str):
    product_data = db.products.find_one({"_id": ObjectId(product_id)})
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")
    product = Product(**product_data)
    product.id_produk = str(product_data["_id"])
    return product

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: str, product: ProductInput):
    product_data = product.dict()
    result = db.products.update_one({"_id": ObjectId(product_id)}, {"$set": product_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    product.id_produk = product_id
    return product

@app.delete("/products/{product_id}", response_model=dict)
def delete_product(product_id: str):
    result = db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}

# Order CRUD
class OrderInput(BaseModel):
    id_transaction: str = ""
    id_user: str
    produk_purchased: List[ProductOrder]
    is_paid: bool
    is_sent: bool

@app.post("/orders/", response_model=OrderInput)
def create_order(order: OrderInput):
    order_data = order.dict()
    total_harga = 0
    total_berat = 0
    for produk in order.produk_purchased:
        product_data = db.products.find_one({"_id": ObjectId(produk.id_produk)})
        if product_data is None:
            raise HTTPException(status_code=404, detail="Product not found")
        if product_data["stok"] < produk.jumlah:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        total_harga += product_data["harga_produk"] * produk.jumlah
        total_berat += product_data["berapa_kilo"] * produk.jumlah
        
    order_data["total_harga"] = total_harga
    order_data["total_berat"] = total_berat
    result = db.orders.insert_one(order_data)   
    order.id_transaction = str(result.inserted_id)
    return order

@app.get("/orders/", response_model=List[Order])
def read_orders(skip: int = 0, limit: int = 100):
    orders = []
    for order_data in db.orders.find().skip(skip).limit(limit):
        order = Order(**order_data)
        order.id_transaction = str(order_data["_id"])
        orders.append(order)
    return orders

@app.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: str):
    order_data = db.orders.find_one({"_id": ObjectId(order_id)})
    if not order_data:
        raise HTTPException(status_code=404, detail="Order not found")
    order = Order(**order_data)
    order.id_transaction = str(order_data["_id"])
    return order

@app.delete("/orders/{order_id}", response_model=dict)
def delete_order(order_id: str):
    result = db.orders.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted"}

# Payment Order
@app.post("/orders/{order_id}/pay", response_model=Order)
def pay_order(order_id: str):
    result = db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"is_paid": True}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    order_data = db.orders.find_one({"_id": ObjectId(order_id)})
    order = Order(**order_data)
    order.id_transaction = str(order_data["_id"])
    return order

# Sent Order
@app.post("/orders/{order_id}/send", response_model=Order)
def send_order(order_id: str):
    result = db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"is_sent": True}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    order_data = db.orders.find_one({"_id": ObjectId(order_id)})
    order = Order(**order_data)
    order.id_transaction = str(order_data["_id"])
    return order

# Create Order Tracking
class OrderTrackingInput(BaseModel):
    id_transaction : str
    status: str
    history: List[OrderTrackingItem]

@app.post("/order-tracking/", response_model=OrderTracking)
def create_order_tracking(order_tracking: OrderTrackingInput):
    order_tracking_data = order_tracking.dict()
    result = db.order_tracking.insert_one(order_tracking_data)
    return order_tracking

# Track Order
@app.get("/order-tracking/{order_id}", response_model=OrderTracking)
def track_order(order_id: str):
    order_tracking_data = db.order_tracking.find_one({"id_transaction": order_id})
    if not order_tracking_data:
        raise HTTPException(status_code=404, detail="Order Tracking not found")
    order_tracking = OrderTracking(**order_tracking_data)
    return order_tracking

# User CRUD
class UserInput(BaseModel):
    id_user : str
    nama_user: str
    username_telegram: str
    last_active: str

@app.post("/users/", response_model=User)
def create_user(user: UserInput):
    user_data = user.dict()
    result = db.users.insert_one(user_data)
    return user

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: str):
    user_data = db.users.find_one({"id_user": user_id})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    user = User(**user_data)
    user.id_user = user_id
    return user

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: str, user: UserInput):
    user_data = user.dict()
    result = db.users.update_one({"id_user": user_id}, {"$set": user_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    user.id_user = user_id
    return user

@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: str):
    result = db.users.delete_one({"id_user": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}

class CartItem(BaseModel):
    id_produk: str
    jumlah: int

class CartInput(BaseModel):
    id_cart: str = ""
    id_user: str
    produk_purchased: List[CartItem]

@app.post("/carts/", response_model=CartInput)
def create_cart(cart: CartInput):
    total_harga = 0
    total_berat = 0
    cart_data = cart.dict()
    for item in cart.produk_purchased:
        product_data = db.products.find_one({"_id": ObjectId(item.id_produk)})
        if product_data is None:
            raise HTTPException(status_code=404, detail="Product not found")
        total_harga += product_data["harga_produk"] * item.jumlah
        total_berat += product_data["berapa_kilo"] * item.jumlah
    cart_data["total_harga"] = total_harga
    cart_data["total_berat"] = total_berat
    result = db.carts.insert_one(cart_data)
    cart.id_cart = str(result.inserted_id)
    return cart

@app.get("/carts/", response_model=List[Cart])
def read_carts(skip: int = 0, limit: int = 100):
    carts = []
    for cart_data in db.carts.find().skip(skip).limit(limit):
        print(cart_data)
        cart = Cart(**cart_data)
        cart.id_cart = str(cart_data["_id"])
        carts.append(cart)
    return carts

@app.get("/carts/{id_user}", response_model=Cart)
def read_cart(id_user: str):
    cart_data = db.carts.find_one({"id_user": id_user})
    if not cart_data:
        raise HTTPException(status_code=404, detail="Cart not found")
    cart = Cart(**cart_data)
    cart.id_cart = str(cart_data["_id"])
    return cart

@app.put("/carts/{id_user}", response_model=CartInput)
def update_cart(id_user: str, cart: CartInput):
    total_harga = 0
    total_berat = 0
    cart_data = cart.dict()

    # Define cart_id here if it is part of the cart input
    cart_id = cart.id_cart  # Assuming cart.id_cart exists in your Cart model

    result = db.carts.update_one({"id_user": id_user}, {"$set": cart_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cart not found")

    for item in cart.produk_purchased:
        product_data = db.products.find_one({"_id": ObjectId(item.id_produk)})
        if product_data is None:
            raise HTTPException(status_code=404, detail="Product not found")
        total_harga += product_data["harga_produk"] * item.jumlah
        total_berat += product_data["berapa_kilo"] * item.jumlah

    cart_data["total_harga"] = total_harga
    cart_data["total_berat"] = total_berat

    # Use the defined cart_id to update the cart
    results = db.carts.update_one({"_id": ObjectId(cart_id)}, {"$set": cart_data})

    cart.id_cart = str(cart_id)
    return cart


@app.delete("/carts/{id_user}", response_model=dict)
def delete_cart(id_user: str):
    result = db.carts.delete_one({"id_user": id_user})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cart not found")
    return {"message": "Cart deleted"}