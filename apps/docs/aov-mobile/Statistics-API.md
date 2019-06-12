## Statistics

**URL** - `https://staging.artofvisuals.com/api/statistics/photos`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session |

**Accepted Parameters**

No additional parameters are supported for this endpoint.

**Response**

```json
{
  "results": [{
    "date": "YY-MM-DD",
    "average_photos_per_user": int
  }]
}
```

**Errors**

**400** Bad request data
