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

### `/api/auth/social`
* POST
```javascript
{
    "access_token": "",
    "provider": "facebook"
}
```

### `/api/gear`
* GET
* POST
```javascript
{
    "item_make": "",
    "item_model": "",
    "link": "",  // only admins can add
    "public": True/False,
    "reviewed": True/False  // Only admins can add. Used to note that gear is legit
}
```

### `/api/gear/{}`
* GET
* PATCH (only admins can use this endpoint)
```javascript
{
    "item_make": "",
    "item_model": "",
    "link": "",
    "public": True/False,
    "reviewed": True/False
}
```

### `/api/me`
* GET
* PATCH
```javascript
{
    "age": __,
    "avatar": "",
    "existing_password": "",  // Necessary to update password
    "first_name": "",
    "gear": [##, ##],
    "last_name": "",
    "location": "",
    "password": "",
    "social_name": ""
}
```

### `/api/me/profile`
* GET
* PATCH
```javascript
{
    "user": __,  // Optional
    "bio": "",
    "cover_image": ""
}
```
* POST
```javascript
{
    "bio": "",
    "cover_image": ""
}
```

### `/api/users`
* POST
```javascript
{
    "age": __,
    "avatar": "",
    "email": "",
    "first_name": "",
    "gear": [##, ##],
    "last_name": "",
    "location": "",
    "password": "",
    "social_name": "",
    "username": ""
}
```

### `/api/users/{}`
* GET

### `/api/users/{}/photos`
* GET

### `/api/users/{}/stars`
* DELETE
* POST

### `/api/photo_classifications`
* GET
* POST
```javascript
{
    "classification_type": "category|tag",
    "name": ""
}
```

### `/api/photo_classifications/{}/photos`
* GET

### `/api/photo_feeds`
* GET

### `/api/photo_feeds/{}/photos`
* GET

### `/api/photos`
* GET
* POST
```javascript
{
    "category": __,
    "tag": __,
    "user": __,
    "attribution_name": "",
    "gear": [##, ##],
    "geo_location": "POINT (long lat)",
    "image": [file],
    "location": ""
}
```

### `/api/photos/{}`
* DELETE
* GET
* PATCH (only for superusers)
```javascript
{
    "category": __,
    "gear": [##, ##],
    "tag": __,
    "attribution_name": "",
    "location": ""
}
```

### `/api/photos/{}/stars`
* DELETE
* POST