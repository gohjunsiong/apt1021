from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime

app = Flask(__name__)

# 模擬數據
menu = [
    {'id': 1, 'name': '披薩', 'price': 100},
    {'id': 2, 'name': '漢堡', 'price': 50},
    {'id': 3, 'name': '義大利麵', 'price': 80},
]

orders = []
deliveries = []
reviews = []

# 客戶查看菜單
@app.route('/')
def index():
    return render_template('index.html', menu=menu)

# 客戶下單
@app.route('/order', methods=['POST'])
def place_order():
    data = request.json
    order = {
        'id': len(orders) + 1,
        'customer': data['customer'],
        'items': data['items'],
        'total': sum(item['price'] * item['quantity'] for item in data['items']),
        'status': '待處理',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    orders.append(order)
    return jsonify({"message": "訂單已成功提交", "order_id": order['id']}), 201

# 餐廳商家確認訂單
@app.route('/confirm_order/<int:order_id>', methods=['POST'])
def confirm_order(order_id):
    order = next((o for o in orders if o['id'] == order_id), None)
    if order:
        order['status'] = '已確認'
        return jsonify({"message": "訂單已確認"}), 200
    return jsonify({"message": "訂單未找到"}), 404

# 餐廳商家通知取餐
@app.route('/notify_pickup/<int:order_id>', methods=['POST'])
def notify_pickup(order_id):
    order = next((o for o in orders if o['id'] == order_id), None)
    if order and order['status'] == '已確認':
        order['status'] = '待取餐'
        deliveries.append(order)
        return jsonify({"message": "已通知取餐"}), 200
    return jsonify({"message": "訂單未找到或未確認"}), 404

# 送貨小哥查看待送訂單
@app.route('/deliveries')
def view_deliveries():
    return jsonify(deliveries)

# 送貨小哥接單
@app.route('/accept_delivery/<int:order_id>', methods=['POST'])
def accept_delivery(order_id):
    delivery = next((d for d in deliveries if d['id'] == order_id), None)
    if delivery:
        delivery['status'] = '已接單'
        return jsonify({"message": "已接單"}), 200
    return jsonify({"message": "訂單未找到"}), 404

# 送貨小哥取貨
@app.route('/pickup_delivery/<int:order_id>', methods=['POST'])
def pickup_delivery(order_id):
    delivery = next((d for d in deliveries if d['id'] == order_id), None)
    if delivery and delivery['status'] == '已接單':
        delivery['status'] = '已取貨'
        return jsonify({"message": "已取貨"}), 200
    return jsonify({"message": "訂單未找到或未接單"}), 404

# 送貨小哥送達簽收
@app.route('/complete_delivery/<int:order_id>', methods=['POST'])
def complete_delivery(order_id):
    delivery = next((d for d in deliveries if d['id'] == order_id), None)
    if delivery and delivery['status'] == '已取貨':
        delivery['status'] = '已送達'
        return jsonify({"message": "訂單已送達"}), 200
    return jsonify({"message": "訂單未找到或未取貨"}), 404

# 客戶給評
@app.route('/review', methods=['POST'])
def add_review():
    data = request.json
    review = {
        'order_id': data['order_id'],
        'rating': data['rating'],
        'comment': data['comment']
    }
    reviews.append(review)
    return jsonify({"message": "評價已提交"}), 201

# 平台結算
@app.route('/settlement')
def settlement():
    # 這裡應該實現實際的結算邏輯
    return jsonify({"message": "結算完成"}), 200

if __name__ == '__main__':
    app.run(debug=True)
