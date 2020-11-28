# interview-zonar
zonar take home interview


# Questions:
1. I've created a private github repo for this and can share it with anyone who needs to see it. Is there a time by which the solution should be submitted?
2. Can a user have one or many wishlists?
3. Would we ever care to know more about wishlists (e.g. name and created on or last modified datetimes)?
4. Should books be unique within a wishlist (e.g. can't have the same book in a wishlist twice)
5. Do we want an ability to bulk-add books to a user's wishlist?
6. Is retrieval of a wishlist in scope for this assignment?
7. Sort of a general question: what level of polish is expected for this assignment? I see a note about documenting how we would scale our solution. Where on the spectrum of prototype to production-ready is the solution expected to fall?

# Assumptions:

# TODO:
1. Setup DB and first models
    - [x] postgresql via docker-compose
    - [x] Flask-SQLAlchemy
    - [x] User model
    - [x] Book model
2. Setup Wishlist model/table [depends on answers to above questions]
3. Setup Wishlist endpoints
4. ~~Dockerize Flask App~~
5. ~~docker-compose entire application~~
6. Write Up
7. Create "dev" vs. "prod" configurations
8. Linting with black
