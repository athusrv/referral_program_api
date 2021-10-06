# Customer Referral Program API

This is an API to mimic an application supposed to have a customer referral program mechanism in order to acquire new
paying customers

The product requirements are:

- An existing user can create a referral to invite people, via a shareable sign-up link that contains a unique code
- When 5 people sign up using that referral, the inviter gets $10.
- When somebody signs up referencing a referral, that person gets $10 on signup.
    - Signups that do not reference referrals do not get any credit.
- Multiple inviters may invite the same person. Only one inviter can earn credit for a particular user signup. An
  inviter only gets credit when somebody they invited signs up; they do not get credit if they invite somebody who
  already has an account.

## Endpoints

This API expose 4 endpoints:

- `POST /login` to get a JWT for use with protected endpoints
- `POST /signup` for creating a new customer
- `GET /referral_code` which will return the referral code and shareable link for a specific customer given a JWT in the
  Authorization header
- `GET /statement` which will return the customer's account statement given a JWT in the Authorization header

### POST /login

This is supposed to return a JWT in the response if the user trying to login can be authenticated. You'll have to submit
a JSON body (Content-Type = application/json) containing `email` and `password` as the example below:

```json
{
  "email": "user@email.com",
  "password": "mypassword"
}
```

Expected responses:

#### 200 OK

The user exists and was authenticated

```json
{
  "token": "string"
}
```

#### 401 UNAUTHORIZED

In case the user wasn't authenticated or if any other error happens

```json
{
  "errors": [
    "string"
  ]
}
```

### POST /signup

This is supposed to create a new customer. You'll have to submit a JSON body (Content-Type = application/json)
containing `name`, `email`, `password` and optionally a `referralCode` as the example below:

```json
{
  "name": "string",
  "email": "string",
  "password": "string",
  "referralCode": "string" // optional
}
```

If you provide a referral code, and it can't be found in the database, then the user registration won't complete and
will throw an error

The property `email` must be unique, so if you provide an email that was already taken, then the user registration won't
complete and will throw an error

Expected responses:

#### 201 CREATED

The resource was created. Response is empty

#### 400 BAD REQUEST

There was request format validation errors

#### 409 CONFLICT

There was a conflict when creating the resource, most likely because the email you provided was already taken

#### 422 UNPROCESSABLE ENTITY

The request is well formatted but one of the required entities couldn't be found in the database, possibly the referral
code

For any errors, the application will return some details, and they will be in format below:

```json
{
  "errors": [
    "string"
  ]
}
```

### GET /statement

This is supposed to return the customer's account statement, so you can use it to make sure the users are getting their
credit given the requirements of the project

You must provide an Authorization header with `Bearer {jwt}`. The JWT will be given to you once you log into the
application

Expected response:

#### 200 OK

```json
[
  {
    "amount": 10.0,
    "currency": "string",
    "description": "string"
  }
]
```

#### 401 UNAUTHORIZED

In case the Authorization header is not present or its content is not valid

### GET /referral_code

This is supposed to return the customer's referral code and a shareable link with the code in it The shareable link can
be opened in the browser so the user will be able to signup using a web view

You must provide an Authorization header with `Bearer {jwt}`. The JWT will be given to you once you log into the
application

Expected response

#### 200 OK

```json
{
  "code": "string",
  "link": "string"
}
```

#### 401 UNAUTHORIZED

In case the Authorization header is not present or its content is not valid