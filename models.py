from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    #USER MODEL
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(25), nullable = False)
    username = db.Column(db.String(25), nullable = False)
    password = db.Column(db.String(40), nullable = False)
    def __init__(self, name,username, password):
        self.name = name
        self.username = username
        self.password = password



class Books(db.Model):
    __tablename__ = "books"
    isbn = db.Column(db.String, primary_key = True)
    title = db.Column(db.String, nullable = False)
    author = db.Column(db.String, nullable = False)
    year = db.Column(db.Integer, nullable = False)
    def __init__(self, isbn,title, author, year):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year

class Reviews(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, nullable = False)
    book_id = db.Column(db.String(25), nullable = False)
    comment = db.Column(db.String(300), nullable = False)
    rating = db.Column(db.Integer, nullable = False)
    def __init__(self, user_id,book_id, comment, rating):
        self.user_id = user_id
        self.book_id = book_id
        self.comment = comment
        self.rating = rating