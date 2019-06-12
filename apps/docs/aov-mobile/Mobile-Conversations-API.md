## Conversations

**URL** - `https://www.staging.artofvisuals.com/api/conversations`

**Accepted Methods**

- GET

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| GET | Session, Token |
| POST | Session, Token |


**Accepted Parameters**

| Parameter | Description | Functionality |
| --------- | ----------- | ------------- |
| participants | Populated with the IDs of users in the conversation. | Returns all conversations that the participants are party to. Can be included multiple times. |

**Response**

```json
{
	"count": int, //Integer value representing number of total results
	"next": "", //Full URL for the next page of results
	"previous": "", //Full URL for the previous page of results
	"results": [
	  {
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
	  }
	] 
}
```

**Errors**

In the event of making a request that has no related data, a response of 200 will be returned with an empty result set.

