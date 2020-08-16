from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
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
        
        #MOVE TO APPLICATION.PY
@app.route("/readcsv")
def main():
    f = open("C:/Users/home/Documents/project1/project1/books.csv")
    reader = csv.reader(f)
    for isbn,title,author,year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added books to books: {isbn} {title} by {author} published in{year}.")
    db.commit()
