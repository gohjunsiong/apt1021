from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"

# 連接資料庫
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="delivery_platform"
)
cursor = conn.cursor(dictionary=True)

# 登入頁面
@app.route("/")
def index():
    return render_template("login.html")

# 登入處理
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    if user:
        session["user_id"] = user["id"]
        session["role"] = user["role"]
        if user["role"] == "restaurant":
            return redirect(url_for("restaurant_dashboard"))
        elif user["role"] == "delivery":
            return redirect(url_for("delivery_dashboard"))
        elif user["role"] == "customer":
            return redirect(url_for("customer_dashboard"))
    return "帳號或密碼錯誤"

# 餐廳商家儀表板
@app.route("/restaurant")
def restaurant_dashboard():
    if "role" in session and session["role"] == "restaurant":
        cursor.execute("SELECT * FROM menu WHERE restaurant_id = %s", (session["user_id"],))
        menu = cursor.fetchall()
        return render_template("restaurant_dashboard.html", menu=menu)
    return redirect(url_for("index"))

@app.route("/add_menu_item", methods=["POST"])
def add_menu_item():
    if "role" in session and session["role"] == "restaurant":
        item_name = request.form["item_name"]
        price = request.form["price"]
        cursor.execute("INSERT INTO menu (restaurant_id, item_name, price) VALUES (%s, %s, %s)", 
                       (session["user_id"], item_name, price))
        conn.commit()
        return redirect(url_for("restaurant_dashboard"))
    return redirect(url_for("index"))

# 送貨小哥儀表板
@app.route("/delivery")
def delivery_dashboard():
    if "role" in session and session["role"] == "delivery":
        cursor.execute("SELECT * FROM orders WHERE status = 'pending'")
        orders = cursor.fetchall()
        return render_template("delivery_dashboard.html", orders=orders)
    return redirect(url_for("index"))

@app.route("/accept_order", methods=["POST"])
def accept_order():
    if "role" in session and session["role"] == "delivery":
        order_id = request.form["order_id"]
        cursor.execute("UPDATE orders SET delivery_id = %s, status = 'accepted' WHERE id = %s",
                       (session["user_id"], order_id))
        conn.commit()
        return redirect(url_for("delivery_dashboard"))
    return redirect(url_for("index"))

# 客戶儀表板
@app.route("/customer")
def customer_dashboard():
    if "role" in session and session["role"] == "customer":
        cursor.execute("SELECT * FROM menu")
        menu = cursor.fetchall()
        return render_template("customer_dashboard.html", menu=menu)
    return redirect(url_for("index"))

@app.route("/place_order", methods=["POST"])
def place_order():
    if "role" in session and session["role"] == "customer":
        cursor.execute("INSERT INTO orders (customer_id, restaurant_id, total_price) VALUES (%s, %s, %s)",
                       (session["user_id"], 1, 50))  # 假設固定餐廳，總價為 50
        conn.commit()
        return redirect(url_for("customer_dashboard"))
    return redirect(url_for("index"))

# 登出
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
