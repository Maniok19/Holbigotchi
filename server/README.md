# filepath: /holbigotchi-backend/holbigotchi-backend/README.md

# Holbigotchi Backend

Holbigotchi is a Tamagotchi-like web application that allows users to care for a virtual pet by solving daily technical challenges. The backend is built using Flask and provides a clean REST API for user management and authentication.

## Features

- **User Registration and Authentication**: Users can register and log in using JWT tokens for secure access.
- **Password Hashing**: User passwords are securely hashed using Bcrypt.
- **SQLite Database**: The application uses SQLite with SQLAlchemy for data persistence.
- **CORS Support**: Cross-Origin Resource Sharing is enabled to allow requests from different origins.
- **Structured API**: The API provides endpoints for user registration, login, and retrieving user information.

## Project Structure

```
holbigotchi-backend
├── app
│   ├── __init__.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── user.py
│   ├── routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── users.py
│   ├── services
│   │   ├── __init__.py
│   │   └── facade.py
│   └── persistence
│       ├── __init__.py
│       └── repository.py
├── config.py
├── run.py
└── requirements.txt
```

## Setup Instructions

1. **Clone the Repository**:
   ```
   git clone <repository-url>
   cd holbigotchi-backend
   ```

2. **Create a Virtual Environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```
   python run.py
   ```

5. **Access the API**: The API will be available at `http://localhost:5000/api/v1/`.

## API Endpoints

- **POST /api/v1/auth/register**: Register a new user.
- **POST /api/v1/auth/login**: Log in and receive a JWT token.
- **GET /api/v1/users/me**: Retrieve the current user's information (requires JWT token).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.