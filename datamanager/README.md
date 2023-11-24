# Flask Movie Management App

This is a Flask-based web application for managing a personal movie collection. Users can register, log in, and add movies to their collection. The movie information is fetched from the Open Movie Database (OMDb) API.

## Features

- User registration and authentication
- Movie addition, deletion, and update
- User-specific movie collections
- Sorting movies by various parameters

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/movie-management-app.git
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables:

    Create a `.env` file in the project root with the following content:

    ```env
    SECRET_KEY=your_secret_key
    ```

    Replace `your_secret_key` with a secret key for Flask.

4. Run the application:

    ```bash
    python app.py
    ```

    Access the app at [http://localhost:5000](http://localhost:5000).

## Usage

1. Register or log in with existing credentials.
2. Explore and manage your movie collection.
3. Add, update, or delete movies as needed.

## Technologies Used

- Flask
- Flask-Login
- Open Movie Database (OMDb) API
- HTML, CSS
- Python

