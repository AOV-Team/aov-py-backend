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

    @task(1)
    def upload_photo(self):
        if self.token:
            with open('apps/common/test/data/photos/1mb.jpg', 'rb') as image:
                self.client.post('/api/photos', data={
                    'category': 8,
                    'public': True,
                }, files={'image': image}, headers={'authorization': 'Token {}'.format(self.token)})

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


class WebsiteUser(HttpLocust):
    host = 'https://staging.artofvisuals.com'
    task_set = NewUser
    min_wait = 1000
    max_wait = 2000
