# Photo API

Base Url: `https://www.staging.artofvisuals.com/api/photos`

## ENDPOINTS

### Photos Top
**URL** - `/top`

**Accepted Methods**
- GET

**Accepted Parameters**

| Parameter| Value| Description|
|--|--|--|
|None| None| Returns all Photos within the last 30 days, ordered by the most number of upvotes. Limited to 100 images.|
|display_page| aov-web-all| Will return all Photos, ordered by a calculated value aggregate from clicks and comments|
|display_page| aov-web-weekly| Will return all Photos, ordered by a calculated value aggregate from clicks and comments, limited by the last week.|
|display_page| picks| Returns all Photos in the AOV Picks feed, ordered by their date of inclusion, descending.|
|display_page| popular| Returns Photos within the last week that have the highest number of actions related|
|data| renders| Returns only the image resource urls in the return object.|
|data| details| Returns all information about the Photo, excluding image resource urls|


**Accepted Data**

None

**Response**

A 200 status code with a response object.

```json
   {
       "next": <paginated url>
       "previous": <paginated url>
       "count": int,
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
               "image_tiny_246": <image url>
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
               "scaled_render": <image url>
               "rank": {
                   "overall": int,
                   "<category name>": int
               }
           }
       ]
   }
```

**Errors**

In the event of requesting a User with an ID that does not exist, a successful response will return with an empty result
set.