import requests
from datetime import datetime

def is_odd(num):
    return num & 0x1

def get_product_data_by_name(product_name, product_data):
    for product in product_data:
        if product["nama_produk"] == product_name:
            return product
    return None

def get_product_data_by_id(product_id, api_url):
    response = requests.get(api_url + "/products/"+product_id)
    if response.status_code == 404:
        return None
    else:
        return response.json()

def user_logic(user_id, username, api_url):
    # Check if user already exists
    response = requests.get(api_url + "/users/" + user_id)
    if response.status_code == 404:
        # User doesn't exist, create a new user
        user_data = {
            "id_user": user_id,
            "nama_user": username,
            "username_telegram": username,
            "last_active": datetime.now().strftime("%Y-%m-%d")
        }
        response = requests.post(api_url + "/users/", json=user_data)
        print('success')
        if response.status_code != 200:
            raise Exception("Failed to create user")
        return "Hi, welcome to our store!"
    else:
        # User already exists, update the user's last active time
        user_data = response.json()
        user_data["last_active"] = datetime.now().strftime("%Y-%m-%d")
        response = requests.put(api_url + "/users/" + user_id, json=user_data)
        if response.status_code != 200:
            raise Exception("Failed to update user")
        return "Welcome back!"

def purchase(extracted_entity, api_url, user_id):
    response = requests.get(api_url + "/products/")
    product_data = response.json()
    if extracted_entity == []:
        text = "What do you want to buy?\nWe have these products:\n"
        for product in product_data:
            text += f"- {product['nama_produk']} - {product['harga_produk']}\n"

        return text, []
    products_with_quantity = []
    extracted_entity_len = len(extracted_entity) #jacket, hat, shirt, 10, 5
    extracted_entity_product = extracted_entity[:extracted_entity_len//2] if not is_odd(extracted_entity_len) else extracted_entity[:extracted_entity_len//2+1]
    extracted_entity_quantity = extracted_entity[extracted_entity_len//2:] if not is_odd(extracted_entity_len) else extracted_entity[extracted_entity_len//2+1:]
    for i in range(len(extracted_entity_product)):
        print(extracted_entity[i])
        if i < len(extracted_entity_quantity):
            products_with_quantity.append((extracted_entity_product[i], extracted_entity_quantity[i]))
        else:
            text = "Please specify the quantity for each product"
            return text, []

    text = "Here are the products you want to buy:\n"
    text += "Product\tQuantity\n"
    for product, quantity in products_with_quantity:
        text += f"{product}\t{quantity}\n"

    #post to cart
    #check is there any cart with user_id
    response = requests.get(api_url + "/carts/"+user_id)
    if response.status_code == 200:
        cart_data = response.json()
        cart_data["produk_purchased"] = []
        for product, quantity in products_with_quantity:
            product_data_indexed = get_product_data_by_name(product, product_data)
            if product_data_indexed is None:
                text = "Product not found"
                return text, []
            cart_data["produk_purchased"].append({
                "id_produk": str(product_data_indexed["id_produk"]),
                "jumlah": quantity
            })
        response = requests.put(api_url + "/carts/"+user_id, json=cart_data)
        return text, products_with_quantity
    else:
        cart_data = {
            "id_user": user_id,
            "produk_purchased": []
        }

        for product, quantity in products_with_quantity:
            product_data_indexed = get_product_data_by_name(product, product_data)
            if product_data_indexed is None:
                text = "Product not found"
                return text, []
            cart_data["produk_purchased"].append({
                "id_produk": str(product_data_indexed["id_produk"]),
                "jumlah": quantity
            })

        response = requests.post(api_url + "/carts/", json=cart_data)

    return text, products_with_quantity

def check_stocks(extracted_entity, api_url):
    response = requests.get(api_url + "/products/")
    product_data = response.json()
    if extracted_entity == []:
        text = "What do you want to check?\nWe have these products:\n"
        for product in product_data:
            text += f"- {product['nama_produk']}\n"

        return text
    
    else:
        text = "Here are the products you want to check:\n"
        text += "Product\tStock\n"
        for product in extracted_entity:
            product_data_indexed = get_product_data_by_name(product, product_data)
            text += f"{product_data_indexed['nama_produk']}\t{product_data_indexed['stok']}\n"

        return text

def product_info_logic(extracted_entity, api_url):
    response = requests.get(api_url + "/products/")
    product_data = response.json()
    if extracted_entity == []:
        text = "What do you want to check?\nWe have these products:\n"
        for product in product_data:
            text += f"- {product['nama_produk']}\n"

        return text
    
    else:
        text = "All of our product are homemade from Indonesia\n"
        text += "Here are the products you want to check:\n"
        text += "Product\tBerat\n"
        for product in extracted_entity:
            print(product)
            
            product_data_indexed = get_product_data_by_name(product, product_data)
            text += f"{product_data_indexed['nama_produk']}\t{product_data_indexed['berapa_kilo']}kg\n"

        return text

def cart_info(api_url, user_id):
    response = requests.get(api_url + "/carts/"+user_id)
    if response.status_code == 404:
        text = "You don't have any cart"
        return text
    else:
        cart_data = response.json()
        text = "Here are the products you want to buy:\n"
        text += "Product\tQuantity\n"
        for product in cart_data["produk_purchased"]:
            product_data = get_product_data_by_id(product["id_produk"], api_url)
            text += f"{product_data['nama_produk']}\t{product['jumlah']}\n"
        text += f"Total Price: {cart_data['total_harga']}\n"
        text += f"Total Weight: {cart_data['total_berat']}kg\n"
        text += "type 'checkout' to checkout your cart"
        return text

def checkout_logic(api_url, user_id):
    response = requests.get(api_url + "/carts/"+user_id)
    if response.status_code == 404:
        text = "You don't have any cart"
        return text
    else:
        cart_data = response.json()
        #post to order
        order_data = {
            "id_user": user_id,
            "produk_purchased": cart_data["produk_purchased"],
            "is_paid": True,
            "is_sent": True
        }
        response = requests.post(api_url + "/orders/", json=order_data)
        data = response.json()
        print(data)
        if response.status_code != 200:
            return "Failed to checkout"

        #delete cart
        response = requests.delete(api_url + "/carts/"+user_id)

        text = "Your order has been placed\n"
        text += f"it's the transaction id: {data['id_transaction']}\n"
        text += f"please on pay our virtual account bank dummy 12345678910\n"
        text += f"with the total price: {cart_data['total_harga']}\n"

        #post to order tracking
        order_tracking_data = {
            "id_transaction": data["id_transaction"],
            "status": "Order Placed",
            "history": [
                {
                    "status": "Order Placed",
                    "place": "Online"
                }
            ]
        }

        response = requests.post(api_url + "/order-tracking/", json=order_tracking_data)

        return text

def track_order_logic(extracted_entity, api_url):
    if len(extracted_entity) == 0:
        text = "Please specify the order id"
        return text

    response = requests.get(api_url + "/order-tracking/"+extracted_entity[0])
    print(response.json())
    if response.status_code == 404:
        text = "Order not found"
        return text
    else:
        order_tracking_data = response.json()
        text = "Here is your order tracking:\n"
        text += f"Status: {order_tracking_data['status']}\n"
        text += "History:\n"
        for history in order_tracking_data["history"]:
            text += f"{history['status']}\t{history['place']}\n"
        return text