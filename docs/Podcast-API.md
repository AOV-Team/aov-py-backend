# Podcast API

Base URL: `https://www.staging.artofvisuals.com/api/aov-web/podcast`

## ENDPOINTS

### Get Featured
**URL** - `/get_featured`

**Accepted Methods**
- POST - JSON/Multipart

**Accepted Data**
```javascript
{
   // Required fields
   "email": "",
   "full_name": "",
   "location": ""
   
   // Optional Fields
   "story": "",
   "image": <image>,
   "instagram_handle": "", // Max 30 characters, including @
   "camera": [],  // Array of individual models, e.g ["Sony A7III", "Canon 7"]
   "audio_sample": <audio> // Coming Soon!
}
```

**Response**

Empty data, with a 200 Status Code.

**Errors**

All errors will return a Status Code of 400 and contain a `message` field in the
returned data detailing what failed.


### Episodes
**URL** - `/episodes`

** Accepted Methods**
- GET

**Accepted Parameters**

| Parameter | Functionality |
| --------- | ------------- |
| published_after | Return all Episodes published after the specified date - YYYY-MM-DD |
| published_before| Return all Episodes published before the specified date - YYYY-MM-DD |
| number | Return the Episode with the specified episode number |
| title | Return Episode's containing the word or phrase, case insensitive. |
| page_size | The number of Episodes to return in a single response. Default is 12, max is 90. |

**Sample URL with Parameters**

`https://www.staging.artofvisuals.com/api/podcast/episodes?published_before=2019-02-07`

**Response**

```javascript
{
	"count": int //Integer value representing number of total results
	"next": "", //Full URL for the next page of results
	"previous": "", //Full URL for the previous page of results
	"results": [] //Array of Episode objects, default length of 12, max length of 90
}
```

**Errors**

All errors will return a Status Code of 400 and contain a `message` field in the
returned data detailing what failed.

