#!/usr/local/bin/python
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

# 連接MariaDB
try:
    conn = mysql.connector.connect(
        user="root",
        password="",
        host="localhost",
        port=3306,
        database="delivery_platform"
    )
    cursor = conn.cursor(dictionary=True)
except mysql.connector.Error as e:
    print(e)
    print("Error connecting to DB")
    exit(1)

# 餐廳上架菜單項目
def add_menu_item(restaurant_id, item_name, description, price):
    sql = "INSERT INTO menu (restaurant_id, item_name, description, price) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (restaurant_id, item_name, description, price))
    conn.commit()
    print("菜單項目已新增")

# 顧客下訂單
def place_order(customer_id, restaurant_id, items):
    total_price = 0
    for item in items:
        # 確認菜單項目存在
        cursor.execute("SELECT price FROM menu WHERE id = %s", (item['menu_id'],))
        menu_item = cursor.fetchone()
        if not menu_item:
            return {"message": "菜單項目不存在"}

        total_price += menu_item["price"] * item["quantity"]

    # 建立訂單
    sql = "INSERT INTO orders (customer_id, restaurant_id, total_price) VALUES (%s, %s, %s)"
    cursor.execute(sql, (customer_id, restaurant_id, total_price))
    order_id = cursor.lastrowid

    # 插入訂單詳細
    for item in items:
        cursor.execute("SELECT price FROM menu WHERE id = %s", (item['menu_id'],))
        menu_item = cursor.fetchone()
        sql = "INSERT INTO order_items (order_id, menu_id, quantity, price) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (order_id, item['menu_id'], item['quantity'], menu_item["price"]))

    conn.commit()
    return {"message": "訂單已建立", "order_id": order_id}

# 顧客查看訂單
def view_orders(customer_id):
    sql = "SELECT id, status, total_price, created_at FROM orders WHERE customer_id = %s"
    cursor.execute(sql, (customer_id,))
    return cursor.fetchall()

# 送貨小哥接單
def accept_order(delivery_id, order_id):
    sql = "UPDATE orders SET delivery_id = %s, status = 'in_delivery' WHERE id = %s AND status = 'pending'"
    cursor.execute(sql, (delivery_id, order_id))
    conn.commit()
    return {"message": "訂單已接單"}

# 送貨小哥查看配送中的訂單
def view_delivery_orders(delivery_id):
    sql = "SELECT o.id, o.status, o.total_price, o.created_at FROM orders o WHERE o.delivery_id = %s AND o.status = 'in_delivery'"
    cursor.execute(sql, (delivery_id,))
    return cursor.fetchall()

# 平台結算餐廳
def settle_payment(platform_id, restaurant_id):
    sql = "SELECT SUM(o.total_price) AS total_amount FROM orders o WHERE o.restaurant_id = %s AND o.status = 'completed'"
    cursor.execute(sql, (restaurant_id,))
    result = cursor.fetchone()
    if result:
        total_amount = result['total_amount']
        sql = "INSERT INTO platform_settlement (platform_id, restaurant_id, total_amount) VALUES (%s, %s, %s)"
        cursor.execute(sql, (platform_id, restaurant_id, total_amount))
        conn.commit()
        return {"message": "結算成功", "total_amount": total_amount}
    return {"message": "未找到有效訂單"}

# 平台查看所有訂單
def view_all_orders():
    sql = "SELECT o.id, o.customer_id, o.restaurant_id, o.total_price, o.status FROM orders o"
    cursor.execute(sql)
    return cursor.fetchall()

# 平台查看結算狀況
def view_settlement():
    sql = "SELECT * FROM platform_settlement"
    cursor.execute(sql)
    return cursor.fetchall()

# 範例使用

# 1. 顧客下訂單
order_items = [{'menu_id': 1, 'quantity': 2}]  # 點兩份牛排
order_response = place_order(customer_id=1, restaurant_id=1, items=order_items)
print(order_response)

# 2. 顧客查看所有訂單
orders = view_orders(customer_id=1)
print(orders)

# 3. 送貨小哥接單
delivery_response = accept_order(delivery_id=1, order_id=1)
print(delivery_response)

# 4. 送貨小哥查看配送中的訂單
delivery_orders = view_delivery_orders(delivery_id=1)
print(delivery_orders)

# 5. 平台結算餐廳
settle_response = settle_payment(platform_id=1, restaurant_id=1)
print(settle_response)

# 6. 平台查看所有訂單
all_orders = view_all_orders()
print(all_orders)

# 7. 平台查看結算狀況
settlement_status = view_settlement()
print(settlement_status)
