# Library Management System

## Overview

This web application allows you to manage a library's collection of books and authors. With this system, you can:

- Add, view, and delete books and authors.
- Search and sort through the library's collection.
- View detailed information about each book and author.

## Features

- **Book Management:** Add, view, and delete books.
- **Author Management:** Add, view, and delete authors.
- **Book Details:** View information about each book including the cover image.
- **Author Details:** View information about each author and their books.
- **Search and Sort:** Easily search and sort books by title or author.

## Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/library-management-system.git
    ```

2. **Navigate to the Project Directory**

    ```bash
    cd library-management-system
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up the Database**

    ```bash
    flask db upgrade
    ```

5. **Run the Application**

    ```bash
    flask run
    ```

    Visit `http://127.0.0.1:5000/` in your web browser to start using the application.

## Usage

- **Home Page:** View and manage books.
- **Add Author/Book:** Add new entries to the database.
- **View Details:** Click on book titles or author names to see more details.
- **Delete:** Remove books or authors from the database.

## Contributing

1. **Fork the Repository**
2. **Create a Feature Branch**
3. **Make Changes and Commit**
4. **Push and Create a Pull Request**

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Open Library](https://openlibrary.org/)
