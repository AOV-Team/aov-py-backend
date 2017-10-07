# AOV Backend
AOV's Django backend. Uses Python 3.5.2 and PostgreSQL w/ PostGIS extension. This project is Vagrant-compatible to
ensure a consistent dev environment that more closely mimics the production environment.

## Getting Started
1. Make sure Vagrant is installed
2. `cd` to project root
3. Run `vagrant up` to create VM
4. `vagrant ssh` to access VM
5. In SSH, `workon backend` to enable the virtual environment and go to project root
6. Run `runserver` alias to start Django dev server and map to `http://localhost:8000`

## Additional files
Make sure the following files are in the project directory before running the project:
* ./aov_dev.pem (for APNS)

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

### `/api/gear`, `/api/gear?item_make=`, `/api/gear?item_model=`, `/api/gear?item_make=&item_model=`
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

### `/api/marketplace/users`
* POST
```javascript
{
    "email": "",
    "password": "",
    "username": ""
}
```

### `/api/marketplace/users/activate`
* POST
```javascript
{
    'code': uuid
}

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

### `/api/users/{}`, `/api/users/{}?username=`
* GET

### `/api/users/{}/following`
* GET

### `/api/users/{}/location`
* GET
* POST
```javascript
{
    "location": "",
    "geo_location": "POINT (long lat)"
}
```

### `/api/users/{}/photos`
* GET

### `/api/users/{}/profile`
* GET

### `/api/users/{}/stars`
* DELETE
* POST

### `/api/statistics/{resource:photos|users}`
* GET

### `/api/devices`, `/api/devices?q=`
* GET (only admins can access this endpoint)
* POST
```javascript
{
    "registration_id": ""
}
```

### `/api/photo_classifications`
* GET
* POST
```javascript
{
    "classification_type": "tag",
    "name": "",
    "icon": [file],
    "category_image": [file],
    "feed_id": _ // PhotoFeed id
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
    "location": "",
    "caption": ""
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

### `/api/photos/{}/caption`
* PATCH
```javascript
{
    "caption": ""
}
```

### `/api/photos/{}/comments`
* GET
* POST
```javascript
{
    "comment": ""
}
```

### `/api/photos/{}/flags`
* POST

### `/api/photos/{}/likes`
* DELETE
* POST

### `/api/photos/{}/stars`
* DELETE
* POST

### `/api/me/actions`
* POST
```javascript
{
    "id": _  // photo id
    "action": "photo_click|photo_imp"
}
```

## Troubleshooting
If certain unit tests are failing due to authentication/timestamp errors (usually Boto/AWS-dependant tests), run 
`sudo ntpdate pool.ntp.org` in your vagrant machine to sync the VM's time.