from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.login()

    def login(self):
        self.client.post("/api/auth", {'email': 'travis@artofvisuals.com', 'password': 'crush2017!'})

    # @task(2)
    # def index(self):
    #     self.client.get("/")

    @task(1)
    def profile(self):
        self.client.get('/api/me', headers={'authorization': 'Token 354a012de983b8079fdba3abd1278853cfc958ff'})


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
