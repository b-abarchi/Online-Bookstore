import os
import csv
import requests

from flask import Flask, session, request, logging, jsonify, render_template, url_for, redirect, flash
from flask_session import Session 
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from werkzeug.security import check_password_hash, generate_password_hash
from models import *


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
app.config["SQLALCHEMY_DATABASE_URI"] =os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))




@app.route("/")
def index():
    return render_template("/index.html")
@app.route("/welcome")
def welcome():
    return render_template("/welcome.html")
@app.route("/reviews")
def reviews():
    return render_template("/reviews.html")

@app.route("/booksearch")
def booksearch():
    return render_template("/booksearch.html")


#REGISTER FORM
@app.route("/register", methods =["GET","POST"])

def register():
    session.clear()
    if request.method=="POST":
        #declare fields
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        
        if password == confirm:
            # Hash user's password to store in DB
            hashedPassword = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
           
           
            #insert user input into database
            db.execute("INSERT INTO users(name, username, password) VALUES(:name, :username, :password )",
                               {"name":name, "username":username, "password":hashedPassword})
            db.commit()
           

            flash("you are registered you can login","success")
            return redirect(url_for('login'))
        else:
            flash("password does not match", "danger")
            return render_template("/register.html")

    return render_template("/register.html")

#LOGIN FORM
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        #GET THE USER INPUT
        username = request.form.get("username")
        passwor = request.form.get("password")
      
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": username})
        
        result = rows.fetchone()
        session["user_id"] = result[0]
      
       # CHECK USERNAME EXISTS AND PASSWORD MATCH
        if result == None or not check_password_hash(result[3], passwor):
            flash("incorrect password","danger")
            return render_template("/login.html")
        else:   
                   # flash("You are now logged in","success")
                    return redirect("/welcome")
        
    return render_template("/login.html")
#LOGOUT 
@app.route("/logout")
def logout():
    """ Log user out """

    #FORGET THE USER
    session.clear()

    #REDIRECT TO THE LOGIN PAGE
    flash("You are now logged out","success")
    return redirect("/login")
#IMPORT
@app.route("/readcsv" , methods=["GET", "POST"])
def readcsv():
 
    if request.method == "POST":
        #ADD A WILDCARD TO THE SEARCH STRING
        query= "%" + request.form.get("search")  + "%"
        query = query.title()
        #SEARCH THE BOOK THROUGH THE DB
        result = db.execute("SELECT * FROM books WHERE isbn LIKE :query OR title LIKE :query OR  author LIKE :query LIMIT 10",
                   
                                {"query": query})
        book = result.fetchall()
        count = result.rowcount
       #ERROR CHECKING
        if result.rowcount is not 0:
           flash("Your book was found","success")
           return render_template("/booksearch.html", count = count, result = result, book = book)
        else:
           flash("Your book was not found, please try again","danger")
           return render_template("/readcsv.html")
    return render_template("/readcsv.html")
#BOOKPAGE
@app.route("/bookpage/<isbn>" , methods=["GET", "POST"])
def bookpage(isbn):
    if request.method == "POST":
        rating = request.form.get("rating")#out of 5.0
        comment = request.form.get("comment")
        #find the ISBN using the id
        row = db.execute("SELECT id FROM books WHERE isbn = :isbn",
                        {"isbn": isbn})
        
        currentUser = session["user_id"]
      
        bookId = row.fetchone() 
        bookId = bookId[0]
        #FIND REVIEWS SUBMITTED BY USER
        result = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
                    {"user_id": currentUser,
                     "book_id": bookId})
        #ALLOW ONE REVIEW PER USER/BOOK
        count = result.rowcount
        if count == 1:
             flash('You already submitted a review for this book', 'warning')
             return render_template("/bookpage.html"  )
        else:
            rating = int(rating)
            #INSERT THE REVIEW TO THE TABLE 
            db.execute("INSERT INTO reviews (user_id, book_id, comment, rating) VALUES \
                        (:user_id, :book_id, :comment, :rating)",
                        {"user_id": currentUser, 
                        "book_id": bookId, 
                        "comment": comment, 
                        "rating": rating})

            # Commit transactions to DB and close the connection
            db.commit()
   
       
            flash('Review submitted!', 'info')
            #--GOODREADS REVIEWS--
        row = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn = :isbn",
                        {"isbn": isbn})
        bookInfo = row.fetchall()
        isbn = bookInfo[0].isbn
        #FIND THE BOOK REVIEW COUNT USING API 
        key = os.getenv("GOODREADS_KEY")
        query = requests.get("https://www.goodreads.com/book/review_counts.json",
                params={"key": key, "isbns": isbn})
        #CONVERT TO JSON AND APPEND REVIEW COUNT TO THE BOOK INFO
        res = query.json()
        res = res['books'][0]
        bookInfo.append(res)
        row = db.execute("SELECT id FROM books WHERE isbn = :isbn",
                        {"isbn": isbn})

        # Save id into variable
        book = row.fetchone() # (id,)
        book = book[0]
        results = db.execute("SELECT users.username, comment, rating \
                            FROM users \
                            INNER JOIN reviews \
                            ON users.id = reviews.user_id \
                            WHERE book_id = :book",
                            {"book": book})

        reviews = results.fetchall()
   
        return render_template("/reviews.html",bookInfo=bookInfo, reviews=reviews)
     
    return render_template("/bookpage.html")
#API GET REQUEST
@app.route("/api/<isbn>", methods=['GET'])
def api_call(isbn):
    #GETTING THE BOOK INFO USING ISBN
    row = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn = :isbn",
                        {"isbn": isbn})
   
    bookInfo = row.fetchone()

    #CREATE A DICTIONARY 
    res2=dict(bookInfo.items())
    #RETRIEVE BOOK REVIEW COUNT AND RATING USING API
    key = os.getenv("GOODREADS_KEY")
    query = requests.get("https://www.goodreads.com/book/review_counts.json",
                params={"key": key, "isbns": isbn})

    #CONVERT TO JSON
    res = query.json()
    res = res['books'][0]

    #APPEND API DATA TO DICT 
    revCount= res['reviews_count']
    avRating= res['average_rating']
    res2.update( {'reviews_count' : revCount} )
    res2.update( {'average_rating' : avRating} )
    # Error checking
    if res is None:   
        return jsonify({"Error": "Invalid book ISBN"}), 422
    return jsonify(res2)

def main():
    db.create_all()
   
if __name__ == "__main__":
  
   main() 
  