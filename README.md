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
containing `name`, `email`, `password` and **optionally** a `referralCode` as the example below:

```json
{
  "name": "string",
  "email": "string",
  "password": "string",
  "referralCode": "string"
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

## My design decisions

### The database

When I started thinking about this challenge, I started with the database architecture in my mind: which tables I'd
create and how they would relate with each other.

Once I had a raw idea of how this would look like I started designing via a database design tool and that's the database
schema that I came up with:

```
                ┌─────────────────────┐
                │customer             │
                ├─────────────────────┤
                │id        integer  PK│
          ┌─────┤name      varchar    ├────────────┐
          │     │email     varchar    │            │
          │     │password  varchar    │            │
          │     └─────────────────────┘            │
          │                                        │
┌─────────┴─────────────────┐            ┌─────────┴───────────┐
│referral_code              │            │account              │
├───────────────────────────┤            ├─────────────────────┤
│code            varchar  PK│            │number    varchar  PK│
│customer        integer  FK│            │customer  integer  FK│
│will_credit_in  integer    │            └───────────┬─────────┘
└───────────────────────────┘                        │
                                         ┌───────────┴──────────────────┐
                                         │statement                     │
                                         ├──────────────────────────────┤
                                         │id           integer        PK│
                                         │currency     varchar        FK├───────────┐
                                         │amount       float            │           │
                                         │description  varchar  NULL    │           │
                                         │account      varchar        FK│    ┌──────┴───────┐
                                         └──────────────────────────────┘    │currency      │
                                                                             ├──────────────┤
                                                                             │id  varchar PK│
                                                                             └──────────────┘
```

I designed the database like this thinking on two aspects:

1. Each table must warehouse values that makes sense to purpose of the table. For example, a dog would never warehouse a
   sound emitted by a cat (lol)
2. Scalability. This database should be able to be easily changed via migrations in case the application needs to grow

The database I chose to work with was PostgreSQL. I don't have any specific reasons to work with this other than the
facts that's the database I've been working most and Heroku provides a free PostgreSQL addon for Heroku apps.

Also, I decided to write migrations. I didn't need it, but thinking about scalability and not using migration is not the
right way to think about it.

### The code

Well, first things first... Let's choose the programming language. With so many around I decided to go with Python since
it's easy to set up an API with it mainly using simple and efficient open source frameworks available

I had two framework options to bootstrap my API: Flask and Django. I picked Flask since I had to write a simple and yet
efficient API, and Flask, in my opinion, is awesome because it's light and there are many libraries around that serves a
plugin to Flask. So, basically Flask gives you just what you need to create a simple API, nothing more than that. Also,
I thought about the project requirement that I had to write as much code as I could even if I had to use frameworks or
libraries, so less is more!

When writing this code I set some expectations:

1. My API must have a separation between the controllers, business rules (services) and database. This will make my code
   easy to understand and be well organized
2. Controllers should at any hypothesis touch the database directly. This is a job for the services
3. Controllers should not handle the security part of the code. This should be a dedicated layer to do this job
4. Controllers will be responsible for validating the request and calling the service only

### Frameworks & Libraries

While I had to write as much code as I could, there are some subjects when you're creating an API that doesn't make
sense to not choose a framework for it. It's the case of API bootstrapping, serialization and validation, database ORM,
security related stuff like encryption and JWT creation and optionally a migration library and also mock libraries if
you're working with unit tests which is the case of this project.

So, the frameworks I chose were:

- Flask: API bootstrapping since it's easy, light and simple
- marshmallow: For serialization and validation since it gives me the ability transform JSON to classes and vice versa
  while still providing fancy validation tools
- SQLAlchemy: The most popular ORM for Python
- pyjwt and pycryptodome: For managing JWT and do some encryption stuff respectively
- alembic: For database migrations
- alchemy-mock: For mocking the SQLAlchemy ORM
- faker: Useful functions for faking text, numbers, passwords...

## How to build and run this API

There are two ways to do it. They are:

### Docker

You can also use the Docker file along with the docker-compose.yml that is available by simply doing:

```shell
docker-compose up -d referral_program_api
```

### Live API

I created a Heroku app for this as well which is the easiest option to start working with this.

The app URL is: https://referral-program-api.herokuapp.com/

## Postman

I've also included a Postman collection in the `postman` folder with the calls for this API. Just import them into your
Postman and you'll have everything setup to start playing with this API. It's currently pointing to the Heroku app