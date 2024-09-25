from pydantic import BaseModel, field_validator
from typing import List
from datetime import datetime

# Product model
class Product(BaseModel):
    id_produk: str = ""
    nama_produk: str
    harga_produk: float
    stok: int
    berapa_kilo: float

class ProductOrder(BaseModel):
    id_produk: str
    jumlah: int

# Order model
class Order(BaseModel):
    id_transaction: str = ""
    id_user: str
    produk_purchased: List[ProductOrder]
    total_harga: float
    total_berat: float
    is_paid: bool
    is_sent: bool

# Cart model
class Cart(BaseModel):
    id_cart: str
    id_user: str
    produk_purchased: List[dict]
    total_harga: float
    total_berat: float

class OrderTrackingItem(BaseModel):
    status: str
    place: str

# Order Tracking model
class OrderTracking(BaseModel):
    id_transaction: str
    status: str
    history: List[OrderTrackingItem]

# User model
class User(BaseModel):
    id_user: str
    nama_user: str
    username_telegram: str
    last_active: str  # You can use a more specific date/time type

    @field_validator('last_active')
    def validate_last_active(cls, value):
        # Define the expected date format
        date_format = '%Y-%m-%d'
        
        try:
            # Try to parse the date string
            datetime.strptime(value, date_format)
            return value
        except ValueError:
            raise ValueError("Invalid date format. Please use yyyy-mm-dd format for last_active.")