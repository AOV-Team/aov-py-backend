## Me

**URL** - `https://staging.artofvisuals.com/api/me`

**Accepted Methods**

- GET
- PATCH - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Token |
| PATCH | Token |

**Accepted Data**

PATCH

```json
{
  "email": "",
  "age": int,
  "gear": [],
  "username": "",
  "gender": ""
}
```

**Response**

```json
{
  "id": int, 
  "age": int, 
  "avatar": <image url>, 
  "email": "", 
  "first_name": "", 
  "gear": [], 
  "gender": "", 
  "is_admin": true | false, 
  "last_login": datetime,
  "last_name": "", 
  "location": "", 
  "social_name": "", 
  "social_url": "", 
  "username": "", 
  "website_url": ""
}
```

**Errors**

**401** Token Authentication failed

## Actions

**URL** - `https://staging.artofvisuals.com/api/me/actions`

**Accepted Methods**

- POST - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| POST | Token |

**Accepted Data**

```json
{
  "id": int,  // ID of the Photo the action is on
  "action": "photo_click | photo_flag | photo_imp"
}
```

**Response**

A standard HTTP response with status code 200.

**Errors**

**404** Object not found

**400** Action not supported and/or Bad Request data

## Following Photos

**URL** - `https://staging.artofvisuals.com/api/me/following/photos`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |

**Accepted Parameters**

No extra parameters are supported for this endpoint.

**Response**

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [
    {
       "id": int,
       "category": int,
       "gear": [int],
       "tag": [],
       "user": int,
       "attribution_name": "",
       "dimensions": {
           "width": int,
           "height": int
       },
       "image": <image url>,
       "image_blurred": <image url>,
       "image_small": <image url>,
       "image_small_2": <image url>,
       "image_tiny_246": <image url>,
       "image_tiny_272": <image url>,
       "latitude": float,
       "longitude": float,
       "location": "",
       "photo_data": "",
       "photo_feed": [int],
       "user_details": {
           "id": int,
           "age": int,
           "email": "",
           "first_name": "",
           "last_name": "",
           "location": "",
           "social_name": "",
           "username": ""
       },
       "magazine_authorized": bool,
       "caption": "",
       "votes_behind": {
           "<category name>": int
       },
       "comments": int,
       "votes": int,
       "user_voted": {
           "voted": bool
       },
       "user_starred": {
           "starred": bool
       },
       "bts_lens": "",
       "bts_shutter": "",
       "bts_iso": "",
       "bts_aperture": "",
       "bts_camera_settings": "",
       "bts_time_of_day": "",
       "bts_camera_make": "",
       "bts_camera_model": "",
       "bts_photo_editor": "",
       "scaled_render": <image url>,
       "rank": {
           "overall": int,
           "<category name>": int
       }
    }
  ]
}
```

**Errors**

**404** Object does not exist

## Galleries

**URL** - `https://staging.artofvisuals.com/api/me/galleries`

**Accepted Methods**

- POST - JSON
- GET
- PUT - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |
| POST | Session, Token |
| PUT | Session, Token |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| name | Query string | Returns all Galleries whose names contain the string provided. |

**Accepted Data**

```json
{
  "name": "",
  "photos": [] // Array of Photo IDs to include in the Gallery
}
```

**Response**

GET

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [
    {
      "id": int,
      "photo_count": int,
      "name": "",
      "public": bool,
      "user": int
    }
  ]
}
```

POST, PUT

```json
{
  "results": {
    "id": int,
    "photo_count": int,
    "name": "",
    "public": bool,
    "user": int
  }
}
```

**Errors**

**400** Bad request data

## Push Notifications

**URL** - `https://staging.artofvisuals.com/api/me/notifications`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |

**Accepted Parameters**

No extra parameters are supported for this endpoint

**Response**

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [
    {
      "id": int, 
      "message": "", 
      "sender": {}, // Dependent on action value, detailed below
      "created_at": datetime, 
      "viewed": bool, 
      "action": "A | C | D | F | R | T | U", 
      "related_object": {} // Dependent on action value detailed below
    }
  ]
}
```

**Sender for Actions A**

NONE

**Sender for Actions C, D, F, R, T, U**
```json
{
  "id": int, 
  "age": int, 
  "avatar": <image url>, 
  "email": "", 
  "first_name": "", 
  "gear": [], 
  "last_name": "", 
  "location": "",
  "social_name": "",
  "social_url": "", 
  "username": "",
  "website_url": ""
}
```

**Related Objects for Actions A, C, T, U**
```json
{
   "id": int,
   "category": int,
   "gear": [int],
   "tag": [],
   "user": int,
   "attribution_name": "",
   "dimensions": {
       "width": int,
       "height": int
   },
   "image": <image url>,
   "image_blurred": <image url>,
   "image_small": <image url>,
   "image_small_2": <image url>,
   "image_tiny_246": <image url>,
   "image_tiny_272": <image url>,
   "latitude": float,
   "longitude": float,
   "location": "",
   "photo_data": "",
   "photo_feed": [int],
   "user_details": {
       "id": int,
       "age": int,
       "email": "",
       "first_name": "",
       "last_name": "",
       "location": "",
       "social_name": "",
       "username": ""
   },
   "magazine_authorized": bool,
   "caption": "",
   "votes_behind": {
       "<category name>": int
   },
   "comments": int,
   "votes": int,
   "user_voted": {
       "voted": bool
   },
   "user_starred": {
       "starred": bool
   },
   "bts_lens": "",
   "bts_shutter": "",
   "bts_iso": "",
   "bts_aperture": "",
   "bts_camera_settings": "",
   "bts_time_of_day": "",
   "bts_camera_make": "",
   "bts_camera_model": "",
   "bts_photo_editor": "",
   "scaled_render": <image url>,
   "rank": {
       "overall": int,
       "<category name>": int
   }
}
```

**Related Objects for Action F**
```json
{
  "id": int, 
  "age": int, 
  "avatar": <image url>, 
  "email": "", 
  "first_name": "", 
  "gear": [], 
  "last_name": "", 
  "location": "",
  "social_name": "",
  "social_url": "", 
  "username": "",
  "website_url": ""
}
```

**Related Objects for Action D**
```json
{
  "id": int, 
  "sender": int, 
  "recipient": int, 
  "message": "", 
  "index": int, 
  "conversation": int, 
  "created_at": datetime, 
  "read": bool
}
```

## Push Notifications View

**URL** - `https://staging.artofvisuals.com/api/notifications/<id>/view`

**Accepted Methods**

- POST - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| POST | Session, Token |

**Response**

Standard HTTP Response with a status code of 200.

**Errors**

## Profile

**URL** - `https://staging.artofvisuals.com/api/me/profile`

**Accepted Methods**

- POST - JSON
- GET
- PATCH - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Token |
| PATCH | Token |
| POST | Token |

**Accepted Parameters**

No extra parameters are supported for this endpoint.

**Accepted Data**

```json
{
  "bio": "",
  "cover_image": <image>
}
```

**Response**

```json
{
  "user": int,
  "bio": "",
  "cover_image": <image url>
}
```

**Errors**

**404** Object does not exist
**400** Bad request data

## Starred Photos

**URL** - `https://staging.artofvisuals.com/api/me/starred/photos`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |

**Accepted Parameters**

No extra parameters are supported for this endpoint.

**Response**

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [
    {
       "id": int,
       "category": int,
       "gear": [int],
       "tag": [],
       "user": int,
       "attribution_name": "",
       "dimensions": {
           "width": int,
           "height": int
       },
       "image": <image url>,
       "image_blurred": <image url>,
       "image_small": <image url>,
       "image_small_2": <image url>,
       "image_tiny_246": <image url>,
       "image_tiny_272": <image url>,
       "latitude": float,
       "longitude": float,
       "location": "",
       "photo_data": "",
       "photo_feed": [int],
       "user_details": {
           "id": int,
           "age": int,
           "email": "",
           "first_name": "",
           "last_name": "",
           "location": "",
           "social_name": "",
           "username": ""
       },
       "magazine_authorized": bool,
       "caption": "",
       "votes_behind": {
           "<category name>": int
       },
       "comments": int,
       "votes": int,
       "user_voted": {
           "voted": bool
       },
       "user_starred": {
           "starred": bool
       },
       "bts_lens": "",
       "bts_shutter": "",
       "bts_iso": "",
       "bts_aperture": "",
       "bts_camera_settings": "",
       "bts_time_of_day": "",
       "bts_camera_make": "",
       "bts_camera_model": "",
       "bts_photo_editor": "",
       "scaled_render": <image url>,
       "rank": {
           "overall": int,
           "<category name>": int
       }
    }
  ]
}
```

**Errors**

If there are no starred photos, a 200 response with an empty results set will be returned.
