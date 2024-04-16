# Cipher

## What is the project?

At the moment this project is a web application that allows users to create, update, and delete posts and comments. It also includes user authentication and profile management features. It has a Demo page which showcases an application 
will be complementary to this website and the reason this webapplication is build for to handle subscriptions, users and manage informations for that future application that will run on desktop. For now it doesn't have any functional usecases in the real world.

## What is the tech stack?

The application is built with the following technologies:

- Python: The backend code is written in Python.
- Flask: The web server is built with the Flask framework.
- SQLAlchemy: SQLAlchemy is used for the ORM (Object-Relational Mapping) to interact with the database.
- PostgreSQL: PostgreSQL is used for the database.
- HTML/CSS/JavaScript: The frontend is built with HTML, CSS, and JavaScript.

## How do I set it up locally?

1. Clone the repository to your local machine.
2. Install the required Python packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up the environment variables `DATABASE_URI` and `SECRET_KEY`.
4. Run the application:

    ```bash
    python app.py
    ```

The application will be available at `http://localhost:5000`.

## How do I test it?

Currently, the application does not have a dedicated test suite. However, you can manually test the application by running it locally and using the application's features.

## How do I deploy it?

The application is currently set up to be deployed on Render. Here are the steps to deploy the application:

1. Push your changes to your GitHub repository.
2. In the Render dashboard, create a new Web Service.
3. Connect your GitHub repository and select the branch you want to deploy.
4. Set the build command to `pip install -r requirements.txt` and the start command to `gunicorn app.app`.
5. Add the `DATABASE_URI` and `SECRET_KEY` environment variables.
6. Click "Create Web Service".

Render will automatically build and deploy your application.

You can update you repository and deploy the last commit with the latest changes.