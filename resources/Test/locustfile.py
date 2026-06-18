from locust import HttpUser, task, between
import random

# Menyimpan order_id yang berhasil dibuat agar bisa dites GET dan PUT
ORDER_IDS = []

class OrderProcessingUser(HttpUser):
    # Waktu jeda antar request per user (0.5 - 2 detik)
    wait_time = between(0.5, 2)

    @task(4)
    def create_order(self):
        """Skenario: User membuat pesanan baru"""
        payload = {
            "product": f"Produk Test {random.randint(1, 100)}",
            "quantity": random.randint(1, 5),
            "price": random.choice([50000, 150000, 300000, 500000])
        }
        with self.client.post("/order", json=payload, catch_response=True, name="POST /order") as res:
            if res.status_code == 201:
                data = res.json()
                if "order_id" in data:
                    ORDER_IDS.append(data["order_id"])
                    # Batasi memory list agar tidak kepenuhan
                    if len(ORDER_IDS) > 5000:
                        ORDER_IDS.pop(0)
                res.success()
            else:
                res.failure(f"Error {res.status_code}")

    @task(2)
    def get_order_history(self):
        """Skenario: User melihat riwayat pesanan (Tugas paling berat buat DB)"""
        with self.client.get("/orders", catch_response=True, name="GET /orders") as res:
            if res.status_code == 200:
                res.success()
            else:
                res.failure(f"Error {res.status_code}")

    @task(2)
    def check_order_status(self):
        """Skenario: User mengecek status pesanan spesifik"""
        if not ORDER_IDS:
            return
        order_id = random.choice(ORDER_IDS)
        with self.client.get(f"/order/{order_id}", catch_response=True, name="GET /order/<id>") as res:
            # 404 dianggap sukses karena wajar jika order belum tersinkron atau terhapus
            if res.status_code in (200, 404):
                res.success()
            else:
                res.failure(f"Error {res.status_code}")

    @task(1)
    def update_order(self):
        """Skenario: Admin/Sistem mengupdate status pesanan"""
        if not ORDER_IDS:
            return
        order_id = random.choice(ORDER_IDS)
        status = random.choice(["processing", "completed", "cancelled"])
        with self.client.put(f"/order/{order_id}", json={"status": status}, catch_response=True, name="PUT /order/<id>") as res:
            if res.status_code in (200, 404):
                res.success()
            else:
                res.failure(f"Error {res.status_code}")
