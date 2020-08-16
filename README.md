# Project 1

Web Programming with Python and JavaScript
GENERAL INFORMATION:
In this project, we built a book review website. Users are able to register for the website and then log in using their username and password. Once they log in, they are able to search for books, leave reviews for individual books, and see the reviews made by other people. also using a third-party API by Goodreads, another book review website, user will be able to pull in ratings from a broader audience. Finally, users will be able to query for book details and book reviews programmatically via your website’s API

Features:
Registration

Login & logout 
Import: Provided for you in this project is a file called books.csv, which is a spreadsheet in CSV format of 5000 different books. Each one has an ISBN number, a title, an author, and a publication year. the csv file is converted in import.py and saved in the heruko database

Search:After performing the search, the website displays a list of possible matching result using only part of a title, ISBN, or author name.

Book Page: etails about the book: its title, author, publication year, ISBN number, and any reviews that users have left for the book on the website

Review Submission: On the book page, users can submit a review: consisting of a rating on a scale of 1 to 5, as well as a text component to the review where the user can write their opinion about a book

Goodreads Review Data & APi Access: the website returns a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score

REQUIREMENTS:
we’ll use a database hosted by Heroku, an online web hosting service
PostgreSQL
Python and Flask
Flask-Session
psycopg2-binary
SQLAlchemy
ItsDangerous==0.24
flask_sqlalchemy==2.4.3
visual studio 

Goodreads API
Goodreads is a popular book review website, and we’ll be using their API in this project to get access to their review data for individual books.
You can now use that API key to make requests to the Goodreads API, documented here. In particular, Python code like the below

import requests
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KEY", "isbns": "9781632168146"})
print(res.json())
