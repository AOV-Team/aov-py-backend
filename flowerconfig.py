import os

broker = 'redis://{}:{}/2'.format(os.environ.get('REDIS_HOST', '0.0.0.0'), os.environ.get('REDIS_PORT', 6379))
