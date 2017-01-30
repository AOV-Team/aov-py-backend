import os

password = ''
redis_password = os.environ.get('REDIS_PASSWORD')

if redis_password:
    password = ':{}@'.format(redis_password)

broker = 'redis://{}{}:{}/2'\
    .format(password, os.environ.get('REDIS_HOST', '0.0.0.0'), os.environ.get('REDIS_PORT', 6379))
