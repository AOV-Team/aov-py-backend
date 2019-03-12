# User API

Base Url: `https://www.staging.artofvisuals.com/api/aov-web/`

## ENDPOINTS

### Users Single
**URL** - `/users/<id>`

**Accepted Methods**
- GET

**Accepted Data**

None

**Response**

A 200 status code with a response object.

```javascript
   {
       "id": int,
       "age": int,
       "avatar": <image url>,
       "first_name" "",
       "last_name": "",
       "location": "",
       "social_name": "",
       "username": ""
   }
```

**Errors**

In the event of requesting a User with an ID that does not exist, a successful response will return with an empty result
set.

### User Profile
**URL** - `/users/<id>/profile`

**Accepted Methods**
- GET

**Accepted Data**

None

**Response**

```javascript
   {
       "user": int,
       "bio": "",
       "cover_image": <image url>
   }
```

**Errors**

If a Profile for a User entity that does not exist is requested, an HTTP 404 will be returned.
