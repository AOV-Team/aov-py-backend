## Feedback

**URL** - `https://staging.artofvisuals.com/api/utils/feedback`

**Accepted Methods**

- POST - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| POST | Token |

**Accepted Parameters**

No additionaly parameters supported for this endpoint.

**Accepted Data**

```json
{
  "feedback_type": "appreciation | feature request | bug"
  "message": ""
}
```

**Response**

```json
{
  "user": int, 
  "id": int, 
  "feedback_type": "A | B | F", 
  "message": "", 
  "reply": "",
  "has_reply": bool, 
  "reply_timestamp": datetime
}
```

**Errors**

**400** Bad request data

**401** Authentication failed
