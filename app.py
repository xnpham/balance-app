import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId # Cần thiết để xử lý ID của MongoDB
import datetime

# Tải các biến môi trường từ file .env
load_dotenv()

app = Flask(__name__)

# --- KẾT NỐI MONGODB ---
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database("FinanceData") # Tên database của bạn
transactions_collection = db.get_collection("money-json") # Tên collection (bảng)

print("✅ Successfully connected to MongoDB.")

# --- ĐỊNH NGHĨA CÁC ENDPOINT ---

# Endpoint để thêm một giao dịch mới
@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    data = request.get_json()

    # Kiểm tra dữ liệu đầu vào
    if not data or 'description' not in data or 'amount' not in data or 'type' not in data:
        return jsonify({"error": "Missing data"}), 400

    try:
        new_transaction = {
            "description": data["description"],
            "amount": float(data["amount"]),
            "type": data["type"], # "income" hoặc "expense"
            "createdAt": datetime.datetime.utcnow()
        }
        # Thêm vào database
        result = transactions_collection.insert_one(new_transaction)
        
        # Trả về thông báo thành công với ID của bản ghi mới
        return jsonify({
            "message": "Transaction added successfully",
            "id": str(result.inserted_id)
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint để lấy tất cả các giao dịch trong 30 ngày qua
@app.route("/transactions", methods=["GET"])
def get_transactions():
    try:
        # Lấy thời điểm 30 ngày trước
        thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        # Lọc các transaction có createdAt >= thirty_days_ago
        query = {"createdAt": {"$gte": thirty_days_ago}}
        all_transactions = list(
            transactions_collection.find(query).sort("createdAt", -1)
        )

        # Chuyển đổi ObjectId thành string để có thể gửi qua JSON
        for transaction in all_transactions:
            transaction["_id"] = str(transaction["_id"])

        return jsonify(all_transactions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- CHẠY SERVER ---
if __name__ == "__main__":
    # host='0.0.0.0' để API có thể được truy cập từ mạng bên ngoài (quan trọng cho máy ảo Android)
    app.run(host='0.0.0.0', port=5000, debug=True)