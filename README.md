# Django Phonebook Application

This repository contains a Django application that allows users to upload a phonebook Excel file and perform various tasks on it. This project is designed to run within a Docker container for easy setup and deployment.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

1. Clone this repository to your local machine:

    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```
   

2. Create a .env file in the project root directory with the following environment variables:

    PostgreSQL vars

    - POSTGRES_DB=your_database_name
    - POSTGRES_USER=your_database_user
    - POSTGRES_PASSWORD=your_database_password

    Django vars

    - DEBUG=1
    - SQL_ENGINE=django.db.backends.postgresql
    - SQL_DATABASE=your_database_name
    - SQL_USER=your_database_user
    - SQL_PASSWORD=your_database_password
    - SQL_HOST=database
    - SQL_PORT=5432

Replace your_database_name, your_database_user, and your_database_password with your preferred database configuration.

3. Build and start the Docker containers:

    ```sh
    docker-compose up --build
    ```

This will start the Django application and PostgreSQL database in separate containers.

4. Access the Django application at http://localhost:8000

## Database Setup and Migrations
The PostgreSQL database is set up automatically using the environment variables you provided in the .env file. The Django application will create the necessary database tables when you run migrations.

To apply migrations:

    docker-compose exec app poetry run python manage.py migrate

