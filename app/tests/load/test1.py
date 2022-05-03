from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    def on_start(self):
        pass
        # self.client.post("/login", {"username": "test_user", "password": ""})

    @task
    def films(self):
        self.client.get("/api/v1/films")

    @task
    def genres(self):
        self.client.get("/api/v1/genres")

    # @task
    # def films_search(self):
    #     self.client.get("/api/v1/films/search?query=Lucas")
