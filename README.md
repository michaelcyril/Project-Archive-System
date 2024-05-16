# pams

## Project Archives Management System

### Download the Project

- Clone or download the project from the repository.

### Install Dependencies

- Install all project dependencies using the requirements.txt file by running the following command:

    ```
    pip install -r requirements.txt
    ```

### Update Database Settings

- Open the settings.py file and update the database configuration with your credentials.

### Create Database

- Create a new database for the project.

### Migrate the Database

- Migrate the database tables by running the following command:

    ```
    python manage.py migrate
    ```

### Create Superuser

- Create a superuser account for administrative access by running the following command:

    ```
    python manage.py createsuperuser
    ```

### Load Seed Data

- Load seed data into the database by running the following command:

    ```
    python manage.py loaddata seeders.json
    ```

### Run the Server

- Start the development server by running the following command:

    ```
    python manage.py runserver
    ```

