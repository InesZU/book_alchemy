import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from data_models import db, Author, Book
import os
from dotenv import load_dotenv


# Initialize Flask app
app = Flask(__name__)
# Load environment variables from .env file
load_dotenv()
# Get the current directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'data', 'library.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY')  # Get secret key from environment variable
# Initialize SQLAlchemy with the app
db.init_app(app)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()


def get_cover_image(isbn, title):
    # Create a file-safe title for the image filename
    safe_title = title.lower().replace(' ', '_')  # e.g., "lonesome_dove"

    # Define the local path where the image will be stored
    local_image_path = os.path.join('static', 'covers', f'{safe_title}.jpg')

    # Check if the cover already exists locally
    if os.path.exists(local_image_path):
        return url_for('static', filename=f'covers/{safe_title}.jpg')

    # Otherwise, fetch the cover from the external source and save it locally
    url = f'https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg'
    response = requests.get(url)
    if response.status_code == 200:
        # Save the image locally
        with open(local_image_path, 'wb') as f:
            f.write(response.content)
        return url_for('static', filename=f'covers/{safe_title}.jpg')
    else:
        # Fallback to a placeholder image if the cover is not found
        return url_for('static', filename='covers/placeholder.jpg')


# Home route
@app.route('/')
def home():
    sort_by = request.args.get('sort_by', 'title')  # Default sort by title
    search_query = request.args.get('search', '')  # Default empty search query

    if sort_by not in ['title', 'author']:
        sort_by = 'title'

    query = Book.query
    if search_query:
        query = query.filter(Book.title.ilike(f'%{search_query}%'))

    if sort_by == 'title':
        books = query.order_by(Book.title).all()
    elif sort_by == 'author':
        books = query.join(Author).order_by(Author.name).all()

    return render_template('home.html', books=books)


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

    return render_template('add_author.html')


# Add Book route
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all()  # Query authors to populate dropdown
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

    return render_template('add_book.html', authors=authors)


# Delete Book route
@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author_id = book.author_id

    db.session.delete(book)
    db.session.commit()

    # Check if the author has any other books
    author = Author.query.get(author_id)
    if not author.books:  # No other books by this author
        db.session.delete(author)
        db.session.commit()

    flash(f'Book "{book.title}" has been deleted successfully!', 'success')
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
    cover_image_url = get_cover_image(book.isbn, book.title)  # Use the function to get the cover image URL

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
