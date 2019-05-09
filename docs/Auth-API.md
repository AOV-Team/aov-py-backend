# Auth API

Base URL: `https://www.staging.artofvisuals.com/api/aov-web/auth`

## Endpoints

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
