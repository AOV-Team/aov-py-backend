# AOV Backend
AOV's Django backend.

## Getting Started
1. Clone repo
2. Set up a virtual environment with Python 3.5
3. Run `./scripts/start.sh dev`
4. Create a Postgres DB using credentials from `backend/settings/project_config.py
5. Run `./manage.py migrate`
6. Run `./manage.py createsuperuser`
7. Run `./scripts/install_redis.sh`
8. Run `./scripts/start.sh`
9. Run `./manage.py runserver` in another terminal

## Commands
To create the Django config file: `./scripts/setup.sh {dev|staging|production}`