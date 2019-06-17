## Classifications

**URL** - `https://staging.artofvisuals.com/api/photo_classifications`

**Accepted Methods**

- POST - JSON
- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Not Required |
| POST | Token |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| classification | `category` or `tag` | Returns all classifications of the specified type. |

**Accepted Data**

```json
{
  "name": "",
  "classification_type": "tag | category"
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
      "name": "", 
      "classification_type": "tag | category", 
      "icon": <image url>, 
      "category_image": <image_url>,
      "feed_id": int
    }
  ]
}
```

POST

```json
{
  "id": int, 
  "name": "", 
  "classification_type": "tag | category", 
  "icon": <image url>, 
  "category_image": <image_url>,
  "feed_id": int
}
```

**Errors**

GET 

**400** Bad request data

POST

**400** Bad request data

**401** Token Authentication failed

## Classifications Search

**URL** - `https://staging.artofvisuals.com/api/photo_classifications/search`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| q | Query string | Returns any PhotoClassification object which is of type `tag` and whose name contains the provided query string. |


**Response**

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [
    {
      "id": int, 
      "name": "", 
      "classification_type": "tag", 
      "icon": <image url>, 
      "category_image": <image_url>,
      "feed_id": int
    }
  ]
}
```

**Errors**

If no matching objects found, an empty results set will be returned.

## Classification Photos

**URL** - `https://staging.artofvisuals.com/api/photo_classificiations/<id>/photos`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Not Required |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| data | `renders` or `details` | Returns all Photos for the PhotoClassification. If `renders`, will only return media. If `details`, will only return non-media. |
| classification | `tag` or `category` | Returns Photos for the PhotoClassification with the provided ID and type. |
| order_by | Value to order result set by | Can be set to any field in the object. Defaults to `votes`, descending. |
| length | Integer value to determine size of page | Parameter that allows user to determine size of one page of results. Default is 12, max is 90. |
| display_tab | Can be None or `recent` | If `recent`, ignores length argument and sets order_by to `created_at`, descending. Always returns 100 objects. |

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

**404** Object does not exist

## Feeds

**URL** - `https://staging.artofvisuals.com/api/photo_feeds`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Not Required |

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
      "name": ""
    }
  ]
}
```

**Errors**

If no Feeds exist, an empty results set will be returned.

## Feed Photos

**URL** - `https://staging.artofvisuals.com/api/photo_feeds/<id>/photos`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Not required |

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

## Photos

**URL** - `https://staging.artofvisuals.com/api/photos`

**Accepted Methods**

- POST - MULTIPART
- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |
| POST | Session, Token |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| data | `renders` or `details` | Returns Photos. If `renders`, will return only media. If `details`, will only return non-media data. |
| classification | Integer or name of a category | Returns all Photos that have a matching PhotoClassification name or ID. | 
| geo_location | Coordinates in the form: SW LONG,SW LAT,NE LONG, NE LAT | Creates a geographical box based on coordinates provided and returns all Photos that have a geo_location contained within. |
| location | Name of a location for photos | Returns all Photos whose location field is an exact match for string provided. |


**Accepted Data**

```json
{
  "category": int, // PhotoClassification ID
  "gear": [int],
  "geo_location": "POINT (Long, Lat)",
  "image": <image file>,
  "tags": "#<tag1> #<tag2> | tag1 tag2 tag3",
  "bts_lens": "",
  "bts_shutter": "",
  "bts_iso": "",
  "bts_aperture": "",
  "bts_camera_settings": "",
  "bts_time_of_day": ""
}
```

**Response**

POST
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

GET

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

**400** Bad request data

## Photo Single

**URL** - `https://staging.artofvisuals.com/api/photos/<id>`

**Accepted Methods**

- GET
- DELETE

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Not Required | 
| DELETE | Token |

**Accepted Parameters**

No extra parameters are supported for this endpoint.

**Response**

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

**Errors**

DELETE

**401** Token Authentication failed

**403** User does not own the Photo

**404** Object not found

## Photo Single Caption

**URL** - `https://staging.artofvisuals.com/api/photos/<id>/caption`

**Accepted Methods**

- PATCH - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| PATCH | Session, Token |

**Accepted Parameters**

No additional parameters are supported for this endpoint.

**Accepted Data**

```json
{
  "caption": "",
  "tags": "#tag1 #tag2 | tag1 tag2 tag3"
}
```

**Response**

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

**Errors**

**401** Authentication failed

**400** Bad request data

**404** Object does not exist

## Photo Single Comments

**URL** - `https://staging.artofvisuals.com/api/photos/<id>/comments`

**Accepted Methods**

- POST - JSON
- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |
| POST | Session, Token |

**Accepted Parameters**

No additional parameters are supported for this endpoint.

**Accepted Data**

```json
{
  "comment": "",
  "mentions": [""] // List of mentioned usernames
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
      "comment": "", 
      "user": {}, 
      "photo": "",  // String of the Photo ID 
      "created_at": datetime, 
      "replies": [
         {
            "id": int, 
            "comment": "", 
            "user": {
               "id": int, 
               "age": int, 
               "avatar": <image url>, 
               "email": "", 
               "first_name": "", 
               "gear": [int], 
               "last_name": "", 
               "location": "", 
               "social_name": "",
               "social_url": "", 
               "username": "", 
               "website_url": ""
            }, 
            "created_at": datetime
         }
     ], 
     "mentions": [
        {
           "id": int, 
           "age": int, 
           "avatar": <image url>, 
           "email": "", 
           "first_name": "", 
           "gear": [int], 
           "last_name": "", 
           "location": "", 
           "social_name": "",
           "social_url": "", 
           "username": "", 
           "website_url": ""
        }
     ] 
   }]
}
```

POST

```json
{
   "id": int, 
   "comment": "", 
   "user": {}, 
   "photo": "",  // String of the Photo ID 
   "created_at": datetime, 
   "replies": [
   {
      "id": int, 
         "comment": "", 
         "user": {
            "id": int, 
            "age": int, 
            "avatar": <image url>, 
            "email": "", 
            "first_name": "", 
            "gear": [int], 
            "last_name": "", 
            "location": "", 
            "social_name": "",
            "social_url": "", 
            "username": "", 
            "website_url": ""
         }, 
         "created_at": datetime
      }
   ], 
   "mentions": [
      {
         "id": int, 
         "age": int, 
         "avatar": <image url>, 
         "email": "", 
         "first_name": "", 
         "gear": [int], 
         "last_name": "", 
         "location": "", 
         "social_name": "",
         "social_url": "", 
         "username": "", 
         "website_url": ""
      }
   ] 
}
```

**Errors**

GET

**404** Object not found

POST

**400** Bad request data

## Photo Single Replies

**URL** - `https://staging.artofvisuals.com/api/photos/<id>/comments/<id>/replies`

**Accepted Methods**

- POST - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| POST | Session, Token |

**Accepted Data**

```json
{
  "reply": "",
  "mentions": [""] // Array of mentioned usernames
}
```

**Response**

```json
{
   "id": int, 
   "comment": "", 
   "user": {}, 
   "photo": "",  // String of the Photo ID 
   "created_at": datetime, 
   "replies": [
   {
      "id": int, 
         "comment": "", 
         "user": {
            "id": int, 
            "age": int, 
            "avatar": <image url>, 
            "email": "", 
            "first_name": "", 
            "gear": [int], 
            "last_name": "", 
            "location": "", 
            "social_name": "",
            "social_url": "", 
            "username": "", 
            "website_url": ""
         }, 
         "created_at": datetime
      }
   ], 
   "mentions": [
      {
         "id": int, 
         "age": int, 
         "avatar": <image url>, 
         "email": "", 
         "first_name": "", 
         "gear": [int], 
         "last_name": "", 
         "location": "", 
         "social_name": "",
         "social_url": "", 
         "username": "", 
         "website_url": ""
      }
   ] 
}
```

**Errors**

**400** Bad request data

## Photo Single Details

**URL** - `https://staging.artofvisuals.com/api/photos/<id>/details`

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
  "results": [
    {
      "id": int, 
      "user": int, 
      "category": "", 
      "gear": [int], 
      "tag": [int], 
      "latitude": float, 
      "location": "", 
      "longitude": float, 
      "photo_data": "",
      "photo_feed": [int], 
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

If an invalid ID is requested, returns an empty results set

## Photo Single Flags

**URL** - `https://staging.artofvisuals.com/api/photos/<id>/flags`

**Accepted Methods**

- POST - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| POST | Session, Token |

**Accepted Parameters**

No additional parameters supported for this endpoint.

**Response**

Standard HTTP Response with status 200 or 201.

**Errors**

**401** Authentication failed

**404** Object not found

## Photo Single Media

**URL** - `https://staging.artofvisuals.com/api/photos/<id>/media`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Not Required |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| height | int | Specifies the height for a custom scaled image render. Requires width. |
| width | int | Specifies the width for a custom scaled image render. Requires height. |

**Response**

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [{
    "id": int, 
    "image": <image url>, 
    "image_blurred": <image url>, 
    "image_medium": <image url>, 
    "image_small": <image url>, 
    "image_small_2": <image url>, 
    "image_tiny_246": <image url>,
    "image_tiny_272": <image url>
  }]
}
```

**Response for Custom Render Dimensions**
```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [{
    "id": int,
    "image": <image url>
  }]
}
```

**Errors**

If an invalid ID is requested an empty results set will be returned.

## Photo Single Likes

**URL** - `https://staging.artofvisuals.com/api/photos/<id>/likes`

**Accepted Methods**

- POST - JSON
- DELETE

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| POST | Session, Token |
| DELETE | Session, Token |

**Accepted Parameters**

No additional parameters are supported for this endpoint.

**Response**

Standard HTTP Response with status of 200 or 201

**Errors**

**409** Duplicate exists

**404** Object not found

## Photo Single Stars

**URL** - `https://staging.artofvisuals.com/api/photos/<id>/stars`

**Accepted Methods**

- POST - JSON
- DELETE

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| POST | Session, Token |
| DELETE | Session, Token |

**Accepted Parameters**

No additional parameters are supported for this endpoint.

**Response**

Standard HTTP Response with status of 200 or 201

**Errors**

**409** Duplicate exists

**404** Object not found

## Top Photos

**URL** - `https://staging.artofvisuals.com/api/photos/top`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Not Required |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| None | -- | Returns the most 100 most popular Photos. |
| data | `renders` or `details` | Returns either the media only or non-media only data for the top Photos. |
| display_page | `picks` or `popular` | If set to `picks`, will return the curated Photos hand-picked by AoV. If set to `popular`, will return the most popular Photos in the community. |

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

None

## Photo Single Votes

**URL** - `https://staging.artofvisuals.com/api/photos/<id>/votes`

**Accepted Methods**

- PATCH - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| PATCH | Session, Token |

**Accepted Parameters**

No additional parameters are supported for this endpoint.

**Accepted Data**

```json
{
  "operation": "increment | decrement"
}
```

**Response**

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

**Errors**

**400** Bad request data

**401** Authentication failed

**404** Object not found
