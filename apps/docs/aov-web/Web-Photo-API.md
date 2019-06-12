## Web Photo API

Base Url: `https://www.staging.artofvisuals.com/api/aov-web/photos`

### Photos Top
**URL** - `/top`

**Accepted Methods**
- GET

**Accepted Parameters**

| Parameter| Value| Description|
|---|---|---|
|None| None| Returns all Photos within the last 30 days, ordered by the most number of upvotes. Limited to 100 images.|
|display_page| all| Will return all Photos, ordered by a calculated value aggregate from clicks and comments|
|display_page| weekly| Will return all Photos, ordered by a calculated value aggregate from clicks and comments, limited by the last week.|
|display_page| picks| Returns all Photos in the AOV Picks feed, ordered by their date of inclusion, descending.|
|display_page| popular| Returns Photos within the last week that have the highest number of actions related|
|width|Width of image, e.g 1920| Does nothing by itself. When provided with height parameter, will return a render in the provided size.|
|height|Height of image, e.g. 1080| Does nothing by itself. When provided with width parameter, will return a render in the provided size.|


**Accepted Data**

None

**Response**

A 200 status code with a response object.


**Sample Response Without Width and Height**
```json
   {
       "next": <paginated url>,
       "previous": <paginated url>,
       "count": int,
       "results": [
           {
               "id": int,
               "image": <image url>,
               "image_blurred": <image url>,
               "image_small": <image url>,
               "image_small_2": <image url>,
               "image_tiny_246": <image url>,
               "image_tiny_272": <image url>,
           }
       ]
   }
```

**Sample Response With Width and Height**
```json
   {
       "next": <paginated url>,
       "previous": <paginated url>,
       "count": int,
       "results": [
           {
               "id": int,
               "image": <image url>
           }
       ]
   }
```

**Errors**

This endpoint will always return at least 100 images as it's default behaviors. Any errors outside that need to be
brought to our attention