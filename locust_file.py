from locust import HttpUser, task, between
import random

class MicroserviceTraffic(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(8) # 80% Normal Traffic
    def normal_request(self):
        self.client.get("/process")

    @task(2) # 20% Anomalous Traffic (Brute Force/DoS)
    def attack_simulation(self):
        # Simulate Brute Force in logs
        for _ in range(10):
            self.client.get("/process", headers={"X-Attempt": "Failed-Login"})