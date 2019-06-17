## Discover

Base Url: `https://www.staging.artofvisuals.com/api/aov-web/discover`

### Downloaders
**URL** - `/downloaders`

**Accepted Methods**
- POST - JSON

**Accepted Data**
```json
{
   // Required fields
   "email": "",
   "name": "",
   "location": "",
   "state_sponsor": <id>,
}
```

**Response**

A 200 status code with a response object.

```json
   {
       "downloadable_file": <resource url>
   }
```

**Errors**

All errors will return a Status Code of 400 and contain a `message` field in the
returned data detailing what failed.

### States
**URL** - `/states`

**Accepted Methods**
- GET

**Accepted Data**
None

**Response**

```json
   {
       "next": None,
       "previous": None,
       "count": int,
       "results": [
           {
               "id": int,
               "name": "",
               "fun_fact_1": "",
               "fun_fact_2": "",
               "fun_fact_3": "",
               "fun_fact_4": "",
               "fun_fact_5": "",
               "icon": <image_url>,
               "video_url": <resource_url>
           },
       ]
   }
```

**Errors**

All errors will return a Status Code of 400 and contain a `message` field in the
returned data detailing what failed.

### State Photographers
**URL** - `/states/<id>/photographers`

**Accepted Methods**
- GET

**Accepted Data**
None

**Response**

```json
   {
       "next": None,
       "previous": None,
       "count": int,
       "results": [
           {
               "photographer": {
                   "name": "",
                   "instagram": "",
                   "profile_image": ""
               },
               "state": {
                   "id": int,
                   "name": "",
                   "fun_fact_1": "",
                   "fun_fact_2": "",
                   "fun_fact_3": "",
                   "fun_fact_4": "",
                   "fun_fact_5": "",
                   "icon": <image_url>,
                   "video_url": <resource_url>
               },
               "feature_start": datetime,
               "feature_end": datetime
           }
       ]
   }

```

**Errors**

All errors will return a Status Code of 400 and contain a `message` field in the
returned data detailing what failed.

### State Photos
**URL** - `/states/<id>/photos`

**Accepted Methods**
- GET

**Accepted Data**
None

**Response**

```json
   {
       "next": <paginated url>,
       "previous": <paginated url>,
       "count": int,
       "results": [
           {
               "state": {
                   "id": int,
                   "name": "",
                   "fun_fact_1": "",
                   "fun_fact_2": "",
                   "fun_fact_3": "",
                   "fun_fact_4": "",
                   "fun_fact_5": "",
                   "icon": <image_url>,
                   "video_url": <resource_url>
               },
               "photo": {
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
               },
               "created_at": datetime
           }
       ]
   }
```

**Errors**

All errors will return a Status Code of 400 and contain a `message` field in the
returned data detailing what failed.

### State Sponsors
**URL** - `/states/<id>/sponsors`

**Accepted Methods**
- GET

**Accepted Data**
None

**Response**

```json
   {
       "next": None,
       "previous": None,
       "count": int,
       "results": [
           {
               "sponsor": {
                   "name": "",
                   "social_handle": "",
                   "website": "",
                   "profile_image": <image url>
               },
               "state": {
                   "id": int,
                   "name": "",
                   "fun_fact_1": "",
                   "fun_fact_2": "",
                   "fun_fact_3": "",
                   "fun_fact_4": "",
                   "fun_fact_5": "",
                   "icon": <image_url>,
                   "video_url": <resource_url>
               },
               "sponsorship_start": datetime,
               "sponsorship_end": datetime
           }
       ]
   }
```

**Errors**

All errors will return a Status Code of 400 and contain a `message` field in the
returned data detailing what failed.