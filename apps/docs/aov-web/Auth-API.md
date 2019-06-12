## Authentication

Base URL: `https://www.staging.artofvisuals.com/api/aov-web/auth`

### Social Authentication

**URL** - `/social`

**Accepted Methods**
- POST - JSON

**Accepted Data**
```json
{
   "access_token": "",  // A token granted by the FB SDK on the frontend
   "provider": "facebook"  // Other providers will be added later
}
```

In the above, `access_token` is a token received from Facebook's API, generally attained using their
[Facebook Login integration.](https://developers.facebook.com/docs/facebook-login/web)

**Response**

A 200 status code with a response object.

```json
   {
       "token": ""  // Internal token
   }
```

**Errors**

**409** User already exists and requires login
**400** Bad request data

