## User API

Base Url: `https://www.staging.artofvisuals.com/api/aov-web/`

### Users Single
**URL** - `/users/<id>`

**Accepted Methods**
- GET

**Accepted Data**

None

**Response**

A 200 status code with a response object.

```json
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

```json
   {
       "user": int,
       "bio": "",
       "cover_image": <image url>
   }
```

**Errors**

If a Profile for a User entity that does not exist is requested, an HTTP 404 will be returned.

### TOp Users
**URL** - `/users/top`

**Accepted Methods**
- GET

**Accepted Data**

None

**Response**

```json
   {
       "count": int,
       "next": <resource url>,
       "previous": <resource url>
       "results": [
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
       ]
   }
```

**Errors**

This endpoint should never error out. It should always return at least one user object in the result set.
