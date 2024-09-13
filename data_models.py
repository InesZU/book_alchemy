from flask_sqlalchemy import SQLAlchemy

# Create a SQLAlchemy instance
db = SQLAlchemy()


class Author(db.Model):
    """
    Author model representing the authors in the library.

    Attributes:
        id (int): Primary key, auto-incremented.
        name (str): Name of the author.
        birth_date (date): Author's birth date.
        date_of_death (date): Author's date of death (nullable).
        books (relationship): One-to-many relationship with the Book model.
    """
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
    """
    Book model representing books in the library.

    Attributes:
        id (int): Primary key, auto-incremented.
        isbn (str): Book's ISBN number.
        title (str): Book title.
        publication_year (int): Year of publication.
        author_id (int): Foreign key linking to the Author model.
        author (relationship): Many-to-one relationship with the Author model.
    """
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13))
    title = db.Column(db.String(200))
    publication_year = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    author = db.relationship('Author', back_populates='books')

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', isbn='{self.isbn}')>"

    def __str__(self):
        return (f"Book: {self.title} (ISBN: {self.isbn}), "
                f"Published: {self.publication_year}, Author ID: {self.author_id}")
