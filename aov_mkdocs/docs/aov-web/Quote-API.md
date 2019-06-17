## Quote API

Base Url: `https://staging.artofvisuals.com/api/aov-web`

### Quote
**URL** - `/quotes`

**Accepted Methods**
- GET

**Accepted Data**

None

**Response**

A 200 status code with a response object.

```json
   {
       "count": int,
       "next": <resource url>,
       "previous": <resource url>,
       "results": [
           {
               "quote": "",
               "author": "",
               "display_date": datetime
           }
       ]
   }
```

**Errors**

In the event of requesting a Quote when one has not been set for the day, a successful response with an empty result 
will be returned.

### Quote Subscriber
**URL** - `/quote-subscribers`

**Accepted Methods**
- POST - JSON

**Accepted Data**

```json
    {
        "email": ""
    }
```

**Response**

A 201 status code with a response object.

```json
   {
       "id": 123,
       "email": "",
       "created_at": datetime,
       "modified_at": datetime
   }
```

**Errors**

In the event of submitting a request to create a Quote Subscriber that is malformed, an HTTP 404 response will be
returned with information pertinent to the failure.