## Users

**URL** - `https://staging.artofvisuals.com/api/users`

**Accepted Methods**

- POST - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| POST | Not Required |

**Accepted Parameters**

No additional parameters are supported by this endpoint.

**Accepted Data**

```json
{
    "age": int,
    "avatar": <image>,
    "email": "",
    "first_name": "",
    "last_name": "",
    "location": "",
    "password": "",
    "social_name": "",
    "social_url": "",
    "username": "",
    "website_url": ""
}
```

**Response**

```json
{
  "id": int, 
  "age": int, 
  "first_name": "",
  "last_name": "", 
  "gender": "", 
  "is_admin": bool, 
  "social_name": "", 
  "avatar": <image url>, 
  "social_url": "", 
  "username": "", 
  "email": "", 
  "gear": [int], 
  "website_url": "", 
  "last_login": datetime, 
  "location": ""
}
```

**Errors**

**400** Bad request data

**409** User already exists

## User Single

**URL** - `https://staging.artofvisuals.com/api/users/<id>`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Not Required |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| username | Query String | Returns the user that matches the ID and username. |

**Response**

```json
{
  "id": int, 
  "age": int, 
  "first_name": "",
  "last_name": "", 
  "gender": "", 
  "is_admin": bool, 
  "social_name": "", 
  "avatar": <image url>, 
  "social_url": "", 
  "username": "", 
  "email": "", 
  "gear": [int], 
  "website_url": "", 
  "last_login": datetime, 
  "location": ""
}
```

**Errors**

**404** Object not found

## User Single Blocked

**URL** - `https://staging.artofvisuals.com/api/users/<id>/blocked`

**Accepted Methods**

- POST - JSON
- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |
| POST | Session, Token |

**Accepted Parameters**

No additional parameters are supported by this endpoint.

**Accepted Data**

```json
{
  "user_id": int
}
```

```json
{
  "remove": true
}
```

**Response**

POST

```json
{
  "user": {
      "id": int, 
      "age": int, 
      "first_name": "",
      "last_name": "", 
      "gender": "", 
      "is_admin": bool, 
      "social_name": "", 
      "avatar": <image url>, 
      "social_url": "", 
      "username": "", 
      "email": "", 
      "gear": [int], 
      "website_url": "", 
      "last_login": datetime, 
      "location": ""
  },
  "blocked_by": int
}
```

GET 

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [{
      "id": int, 
      "age": int, 
      "first_name": "",
      "last_name": "", 
      "gender": "", 
      "is_admin": bool, 
      "social_name": "", 
      "avatar": <image url>, 
      "social_url": "", 
      "username": "", 
      "email": "", 
      "gear": [int], 
      "website_url": "", 
      "last_login": datetime, 
      "location": ""
  }]
}
```

## User Conversations

**URL** - `https://staging.artofvisuals.com/api/user/<id>/conversations`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Token |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| participants | int | Returns all conversations in which the provided participants are contributing. Can be used multiple times in a single url. |

**Response**

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [{
    "id": int,
    "participants": [{
      "id": int, 
      "age": int, 
      "first_name": "",
      "last_name": "", 
      "gender": "", 
      "is_admin": bool, 
      "social_name": "", 
      "avatar": <image url>, 
      "social_url": "", 
      "username": "", 
      "email": "", 
      "gear": [int], 
      "website_url": "", 
      "last_login": datetime, 
      "location": ""
    }],
    "latest": {
      "id": int, 
      "sender": int, 
      "recipient": int, 
      "message": "", 
      "index": int, 
      "conversation": int, 
      "created_at": datetime, 
      "read": bool
    },
    "message_count": int
  }]
}
```

## User Conversations Single

**URL** - `https://staging.artofvisuals.com/api/users/<id>/conversations/<id>`

**Accepted Methods**

- DELETE

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| DELETE | Token |

**Accepted Parameters**

No additional parameters are accepted for this endpoint.

**Response**

A standard HTTP Response with a status code of 200 will be returned.

**Errors**

**409** Conversation already deleted

## User Single Following

**URL** - `https://staging.artofvisuals.com/api/users/<id>/following`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Not Required |

**Accepted Parameters**

No additional parameters are supported by this endpoint.

**Response**

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [{
      "id": int, 
      "age": int, 
      "first_name": "",
      "last_name": "", 
      "gender": "", 
      "is_admin": bool, 
      "social_name": "", 
      "avatar": <image url>, 
      "social_url": "", 
      "username": "", 
      "email": "", 
      "gear": [int], 
      "website_url": "", 
      "last_login": datetime, 
      "location": ""
  }]
}
```

**Errors**

**404** Object not found

## Followers

**URL** - `https://staging.artofvisuals.com/api/users/<id>/followers`

**Accepted Methods**

- POST - JSON
- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Not Required |
| POST | Token |

**Accepted Parameters**

No additional parameters are supported by this endpoint

**Response**

Standard HTTP Response with a status code of 201

**Errors**

**401** Authentication failed

**409** Already following

**404** Object not found

## Follower Single

**URL** - `https://staging.artofvisuals.com/api/users/<id>/followers/<id>`

**Accepted Methods**

- DELETE

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| DELETE | Token |

**Accepted Parameters**

No additional parameters are supported by this endpoint.

**Response**

Standard HTTP Response with a status code of 200

**Errors**

**401** Authentication failed

**404** Object not found

## User Galleries

**URL** - `https://staging.artofvisuals.com/api/users/<id>/galleries`

**Accepted Methods**

- POST - JSON
- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |
| POST  | Session, Token |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| name | Query String | Returns Galleries for the specified User with the provided string contained in the Gallery name. |


**Accepted Data**

```json
{
  "name": "",
  "photos": [int] // Optional
}
```

**Response**

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [{
    "id": int, 
    "name": "", 
    "photo_count": int, 
    "public": bool
  }]
}
```

**Errors**

**401** Authentication failed

## User Galleries Single

**URL** - `https://staging.artofvisuals.com/api/users/<id>/galleries/<id>`

**Accepted Methods**

- PUT - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| PUT | Session, Token |

**Accepted Parameters**

No additional parameters are supported by this endpoint.

**Accepted Data**

Any of the following can be done separately or together

```json
{
  "name": "",
  "photos": [int],
  "public": bool
}
```

**Response**

```json
{
  "results": {
    "id": int, 
    "name": "", 
    "photo_count": int, 
    "public": bool
  }
}
```

**Errors**

**400** Bad request data

**401** Authentication failed

**404** Object not found

## Gallery Photos

**URL** - `https://staging.artofvisuals.com/api/users/<id>/galleries/<id>/photos`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |

**Accepted Parameters**

No additional parameters are supported by this endpoint.

**Response**

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [{
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
  }]
}
```

**Errors**

In the event of no Photos in a Gallery, an empty results set will be returned

## Location

**URL** - `https://staging.artofvisuals.com/api/users/<id>/location`

**Accepted Methods**

- POST - JSON
- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Token |
| POST | Token |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| geo_location | Coordinates in the form: SW LONG,SW LAT,NE LONG, NE LAT | Creates a geographical box based on coordinates provided and returns all Photos for the Gallery that have a geo_location contained within.

**Accepted Data**

```json
{
  "location": "",
  "geo_location": "POINT (LONG, LAT)"
}
```

**Response**

```json
{
  "id": int,
  "user": int, 
  "latitude": float, 
  "location": "", 
  "longitude": float, 
  "coordinates": ""
}
```

**Errors**

**400** Bad request data

**401** Authentication failed

## Messages

**URL** - `https://staging.artofvisuals.com/api/users/<id>/messages`

**Accepted Methods**

- POST - JSON
- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Token |
| POST | Token |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| conversation_id | integer | Returns all messages for the associated Conversation ID. |

**Accepted Data**

```json
{
  "message": "",
  "conversation_id": int // Required for sending message in an existing conversation
}
```

**Response**

GET

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [{
      "id": int, 
      "sender": int, 
      "recipient": int, 
      "message": "", 
      "index": int, 
      "conversation": int, 
      "created_at": datetime, 
      "read": bool
  }]
}
```

POST

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

**Errors**

**400** Bad request data

**401** Authentication failed

## Direct Message Read

**URL** - `https://staging.artofvisuals.com/api/users/<id>/messages/<id>/read`

**Accepted Methods**

- POST - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| POST | Token |

**Accepted Parameters**

No additional parameters are supported by this endpoint.

**Response**

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

**Errors**

**401** Authentication failed

**404** Object not found

## User Photos

**URL** - `https://staging.artofvisuals.com/api/users/<id>/photos`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| data | `renders` or `details` | Returns either all media or all non-media data for the Photos. |

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

**Response for Renders**

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [
    {
      "id": int, 
      "image": <image url>, 
      "image_blurred": <image url>, 
      "image_medium": <image url>, 
      "image_small": <image url>, 
      "image_small_2": <image url>, 
      "image_tiny_246": <image url>,
      "image_tiny_272": <image url>
    }
  ]
}
```

**Response for Details**

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [
    {
      "id": int, 
      "user": int, 
      "category": "", 
      "gear": [], 
      "tag": "", 
      "latitude": float, 
      "location": "", 
      "longitude": float, 
      "photo_data": "",
      "photo_feed": "", 
      "caption": "", 
      "bts_lens": "", 
      "bts_shutter": "", 
      "bts_iso": "", 
      "bts_aperture": "",
      "bts_camera_settings": "", 
      "bts_time_of_day": "", 
      "bts_camera_make": "", 
      "bts_camera_model": "",
      "bts_photo_editor": ""
    }
  ]
}
```

**Errors**

**401** Authentication failed

## Profile

**URL** - `https://staging.artofvisuals.com/api/users/<id>/profile`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |

**Accepted Parameters**

No additional parameters are supported by this endpoint.


**Response**

```json
{
  "user": int, 
  "bio": "", 
  "cover_image": <image url>
}
```

**Errors**

**401** Authentication failed

**404** Object not found

## Starred Users

**URL** - `https://staging.artofvisuals.com/api/users/<id>/stars`

**Accepted Methods**

- POST - JSON
- DELETE

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| POST | Session, Token |
| DELETE | Session, Token |

**Accepted Parameters**

No additional parameters supported by this endpoint.

**Response**

Standard HTTP Response with a status code of 200 for DELETE and 201 for POST.

**Errors**

**401** Authentication failed

**404** Object not found

**409** User already starred
