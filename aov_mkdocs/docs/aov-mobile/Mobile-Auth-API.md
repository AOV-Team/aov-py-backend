## Authentication

**URL** - `https://www.staging.artofvisuals.com/api/auth`

**Accepted Methods**

- POST - JSON

- DELETE

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| POST | Not Required |
| DELETE | Not Required |

**Accepted Data**

POST
```json
{
   "email": "",  
   "password": ""
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


## Reset

**URL** - `https://www.staging.artofvisuals.com/api/auth/reset`

**Accepted Methods**

- POST - JSON

- PATCH - JSON

**Authentication**

| Method | Accepted Authentication Types |
| --- | --- |
| POST | Not Required |
| PATCH | Not Required |

**Accepted Data**

POST - Request a password reset code

```json
{
  "email": ""
}
```

PATCH - Submit code with new password to assign
```json
{
   "code": "",
   "password": ""
}
```

**Response**

A 201 status code. Additionally, an email with the password reset code will be sent to the provided email.

PATCH

A 200 response.

**Errors**

POST

**400** Bad request

PATCH

**403** Invalid reset code

**404** User does not exist
