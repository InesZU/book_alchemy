import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from data_models import db, Author, Book
import os
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)
load_dotenv()

# Configure SQLAlchemy and set the secret key from the environment variable
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
        'sqlite:///' + os.path.join(basedir, 'data', 'library.sqlite')
                                        )
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY')
db.init_app(app)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()


def get_cover_image(isbn, title):
    """
    Fetches a book cover image using the ISBN or provides a local placeholder.

    Args:
        isbn (str): The ISBN of the book.
        title (str): The title of the book.

    Returns:
        str: URL of the book cover image or placeholder.
    """
    safe_title = title.lower().replace(' ', '_')
    local_image_path = os.path.join('static', 'covers', f'{safe_title}.jpg')

    if os.path.exists(local_image_path):
        return url_for('static', filename=f'covers/{safe_title}.jpg')

    url = f'https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg'
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_image_path, 'wb') as f:
            f.write(response.content)
        return url_for('static', filename=f'covers/{safe_title}.jpg')
    return url_for('static', filename='covers/placeholder.jpg')


@app.route('/')
def home():
    """
    Home route to display a list of books. Supports sorting by title or author,
    and searching by book title or author name.

    Query Parameters:
        sort_by (str): Sorting option, either 'title' or 'author'. Default is 'title'.
        search (str): Search query to filter books by title or author name.

    Returns:
        Rendered home.html template with the list of books.
    """
    sort_by = request.args.get('sort_by', 'title')  # Default sort by title
    search_query = request.args.get('search', '')  # Default empty search query

    if sort_by not in ['title', 'author']:
        sort_by = 'title'

    # Perform the query
    query = Book.query.join(Author)  # Join with the Author table

    if search_query:
        # Search for books where title or author's name matches the search query
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search_query}%'),
                Author.name.ilike(f'%{search_query}%')
            )
        )

    # Sort the results based on the sort_by parameter
    if sort_by == 'title':
        books = query.order_by(Book.title).all()
    elif sort_by == 'author':
        books = query.order_by(Author.name).all()

    return render_template('home.html', books=books)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Route to add a new author to the library.
    Handles GET for the form and POST to save the author.

    Returns:
        GET: Rendered add_author.html form.
        POST: Redirects to /add_author with success or error messages.
    """
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birth_date']
        date_of_death = request.form.get('date_of_death')

        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date() \
            if birth_date else None
        date_of_death = datetime.strptime(date_of_death, "%Y-%m-%d").date() \
            if date_of_death else None

        existing_author = Author.query.filter_by(name=name).first()
        if existing_author:
            flash(f'Error: Author "{name}" already exists.',
                  'danger')
        else:
            new_author = Author(name=name, birth_date=birth_date,
                                date_of_death=date_of_death)
            db.session.add(new_author)
            db.session.commit()
            flash(f'Author "{new_author.name}" added successfully!',
                  'success')
        return redirect(url_for('add_author'))

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    Route to add a new book to the library.
    Handles GET for the form and POST to save the book.

    Returns:
        GET: Rendered add_book.html form.
        POST: Redirects to /add_book with success or error messages.
    """
    authors = Author.query.all()
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']

        existing_book = Book.query.filter_by(isbn=isbn).first()
        if existing_book:
            flash(f'Error: A book with ISBN "{isbn}" already exists.',
                  'danger')
        else:
            new_book = Book(isbn=isbn, title=title,
                            publication_year=publication_year,
                            author_id=author_id)
            db.session.add(new_book)
            db.session.commit()
            flash(f'Book "{new_book.title}" added successfully!',
                  'success')
        return redirect(url_for('add_book'))

    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    Route to delete a specific book from the library.
    Deletes the author if they have no other books.

    Args:
        book_id (int): ID of the book to delete.

    Returns:
        Redirects to the homepage with a success message.
    """
    book = Book.query.get_or_404(book_id)
    author_id = book.author_id

    db.session.delete(book)
    db.session.commit()

    author = Author.query.get(author_id)
    if not author.books:
        db.session.delete(author)
        db.session.commit()

    flash(f'Book "{book.title}" has been deleted successfully!',
          'success')
    return redirect(url_for('home'))


@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    """
    Route to delete an author and all their books.

    Args:
        author_id (int): ID of the author to delete.

    Returns:
        Redirects to the homepage with a success message.
    """
    author = Author.query.get_or_404(author_id)

    books = Book.query.filter_by(author_id=author_id).all()
    for book in books:
        db.session.delete(book)

    db.session.delete(author)
    db.session.commit()

    flash(f"The author '{author.name}' and all their books "
          f"have been deleted successfully.", 'success')
    return redirect(url_for('home'))


@app.route('/book/<int:book_id>')
def book_details(book_id):
    """
    Route to display details of a specific book.

    Args:
        book_id (int): ID of the book to display.

    Returns:
        Rendered book_details.html page.
    """
    book = Book.query.get_or_404(book_id)
    cover_image_url = get_cover_image(book.isbn, book.title)

    return render_template('book_details.html',
                           book=book, cover_image_url=cover_image_url)


@app.route('/author/<int:author_id>')
def author_details(author_id):
    """
    Route to display details of a specific author.Args:
    author_id (int): ID of the author to display.

    Returns:
        Rendered author_details.html page.
    """
    author = Author.query.get_or_404(author_id)
    return render_template('author_details.html',
                           author=author)


if __name__ == '__main__':
    """
    Entry point of the application. 
    Starts the Flask development server in debug mode.
    """
    app.run(debug=True)