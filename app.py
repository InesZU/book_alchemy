import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from data_models import db, Author, Book
import os

app = Flask(__name__)

# Get the current directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Configure the SQLAlchemy part of the app instance
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'data', 'library.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'HZBATSKLoh4r7ghkfiobmnkkjf'

db.init_app(app)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()


def get_cover_image(isbn):
    url = f'https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg'
    response = requests.get(url)
    if response.status_code == 200:
        return url
    else:
        return 'https://via.placeholder.com/150?text=No+Cover+Available'


# Home route
@app.route('/')
def home():
    sort_by = request.args.get('sort_by', 'title')
    search_query = request.args.get('search', '')

    query = Book.query.join(Author)

    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            (Book.title.ilike(search_term)) |
            (Author.name.ilike(search_term))
        )

    if sort_by == 'author':
        query = query.order_by(Author.name)
    else:
        query = query.order_by(Book.title)

    books = query.all()

    books_data = []
    for book in books:
        books_data.append({
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'cover_image_url': get_cover_image(book.isbn),  # Add cover image URL
            'author_id': book.author.id,  # Add author_id here
        })

    return render_template('home.html', books=books_data)


# Add Author route
@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birth_date']
        date_of_death = request.form.get('date_of_death')

        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date() if birth_date else None
        date_of_death = datetime.strptime(date_of_death, "%Y-%m-%d").date() if date_of_death else None

        existing_author = Author.query.filter_by(name=name).first()
        if existing_author:
            flash(f'Error: Author "{name}" already exists.', 'danger')
        else:
            new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
            db.session.add(new_author)
            db.session.commit()
            flash(f'Author "{new_author.name}" added successfully!', 'success')
        return redirect(url_for('add_author'))

    authors = Author.query.all()
    return render_template('add_author.html', authors=authors)


# Add Book route
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']

        existing_book = Book.query.filter_by(isbn=isbn).first()
        if existing_book:
            flash(f'Error: A book with ISBN "{isbn}" already exists.', 'danger')
        else:
            new_book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
            db.session.add(new_book)
            db.session.commit()
            flash(f'Book "{new_book.title}" added successfully!', 'success')
        return redirect(url_for('add_book'))

    return render_template('add_book.html')


# Delete Book route
@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()

    if not Book.query.filter_by(author_id=author.id).first():
        db.session.delete(author)
        db.session.commit()

    flash(f"The book '{book.title}' has been deleted successfully.", 'success')
    return redirect(url_for('home'))


# Delete Author route
@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)

    # Deleting all books by the author
    books = Book.query.filter_by(author_id=author_id).all()
    for book in books:
        db.session.delete(book)

    # Deleting the author
    db.session.delete(author)
    db.session.commit()

    flash(f"The author '{author.name}' and all their books have been deleted successfully.", 'success')
    return redirect(url_for('home'))


# Book Details route
@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    cover_image_url = get_cover_image(book.isbn)  # Use the function to get the cover image URL

    return render_template('book_details.html',
                           book=book,
                           cover_image_url=cover_image_url)


# Author Detail route
@app.route('/author/<int:author_id>')
def author_details(author_id):
    author = Author.query.get_or_404(author_id)
    return render_template('author_details.html', author=author)


if __name__ == '__main__':
    app.run(debug=True)
