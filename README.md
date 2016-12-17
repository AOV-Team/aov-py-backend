# AOV Backend
AOV's Django backend.

## Getting Started
1. Clone repo
2. Set up a virtual environment with Python 3.5: `virtualenv --python=python3.5 {name}`
3. Run `pip install -r requirements.txt`
4. Run `./scripts/start.sh dev`
5. Create a Postgres DB using credentials from `backend/settings/project_config.py
6. Run `./manage.py migrate`
7. Run `./manage.py createsuperuser`
8. Run `./scripts/install_redis.sh`
9. Run `./scripts/start.sh`
10. Run `./manage.py runserver` in another terminal

## Commands
To create the Django config file: `./scripts/setup.sh {dev|staging|production}`

## Endpoints
### `/api/auth`
* DELETE
* POST 
```javascript
{
    "email": "",
    "password": ""
}
````

### `/api/auth/reset`
* PATCH
```javascript
{
    "code": "",
    "password": ""
}
```
* POST
```javascript
{
    "email": ""
}
```