from locust import HttpLocust, TaskSet, task
import json
import random


class NewUser(TaskSet):
    email = None
    token = None

    def on_start(self):
        """
        When task set starts, register new user

        :return: None
        """
        self.register()
        self.login()

        if self.token:
            self.create_profile()

    @task(1)
    def get_photos(self):
        if self.token:
            response = self.client.get('/api/photos', headers={'authorization': 'Token {}'.format(self.token)})
            # print(response.status_code, response.content)

    def register(self):
        identifier = random.randrange(1000000)
        self.email = 'test-{}@artofvisuals.com'.format(identifier)

        self.client.post('/api/users', {
            'email': self.email,
            'is_active': True,
            'password': 'pass',
            'social_name': '@test-{}'.format(identifier),
            'username': '@test-{}'.format(identifier)
        })

    def login(self):
        response = self.client.post('/api/auth', {
            'email': self.email,
            'password': 'pass',
        })

        if response.status_code == 201:
            content = json.loads(response.content.decode('utf-8'))
            self.token = content['token']

    def create_profile(self):
        with open('apps/common/test/data/photos/cover.jpg', 'rb') as image:
            self.client.post('/api/me/profile', {
                'bio': 'My email is {}'.format(self.email),
                'cover': image
            }, {'authorization': 'Token {}'.format(self.token)})


class WebsiteUser(HttpLocust):
    host = 'https://staging.artofvisuals.com'
    task_set = NewUser
    min_wait = 1000
    max_wait = 2000
