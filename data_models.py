from flask_sqlalchemy import SQLAlchemy

# Create a SQLAlchemy instance
db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)
    books = db.relationship('Book', back_populates='author', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return (f"Author: {self.name}, Born: {self.birth_date}, "
                f"Died: {self.date_of_death or 'N/A'}")


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13))
    title = db.Column(db.String(200))
    publication_year = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

    # Establish a relationship with the Author model
    author = db.relationship('Author', back_populates='books')

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', isbn='{self.isbn}')>"

    def __str__(self):
        return (f"Book: {self.title} (ISBN: {self.isbn}), "
                f"Published: {self.publication_year}, Author ID: {self.author_id}")
