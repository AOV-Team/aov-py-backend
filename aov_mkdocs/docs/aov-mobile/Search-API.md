## Users

**URL** - `https://staging.artofvisuals.com/api/search/users`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |

**Accepted Parameters**

| Parameter | Description | Result |
| --- | --- | --- |
| q | Query string | Any User who has a username, first name, last name, or social name that contains the query string will be returned. |

**Response**

```json
{
  "count": int,
  "next": <resource_url>,
  "previous": <resource_url>,
  "results": [{
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
  }]
}
```

**Errors**

If a query string with no matches is submitted, an empty results set will be returned.
