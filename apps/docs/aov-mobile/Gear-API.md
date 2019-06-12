## Gear

**URL** - `https://www.staging.artofvisuals.com/api/gear`

**Accepted Methods**

- GET
- POST - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |
| POST | Session, Token | 

**Accepted Parameters**

| Paramter | Description | Result |
| --- | --- | --- |
| item_make | query string | Return Gear with an item make similar to the provided string |
| item_model | query string | Return Gear with an item model similar to the provided string |

**Accepted Data**

```json
{
  "item_make": "",
  "item_model": ""
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
      "item_make": "",
      "item_model": "",
      "reviewed": true | false,
      "link": ""
    }
  ]
}
```

POST

```json
{
  "id": int,
  "item_make": "",
  "item_model": "",
  "reviewed": true | false,
  "link": ""
}
```

**Errors**

GET

An empty result set will be returned if there are no matching results.

POST

**400** Badly formed request

## Gear Single

**URL** - `https://www.staging.artofvisuals.com/api/gear/<id>`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |

**Accepted Parameters**

There are no query parameters accepted for this endpoint.

**Response**

```json
{
  "id": int,
  "item_make": "",
  "item_model": "",
  "reviewed": true | false,
  "link": ""
}
```

**Errors**

An empty result set will be returned if there are no matching results.
