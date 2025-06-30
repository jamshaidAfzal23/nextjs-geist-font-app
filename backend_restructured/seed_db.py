import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API base URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

# User data to be created
USER_DATA = {
    "full_name": "Admin User",
    "email": "admin@example.com",
    "password": "TestPassword123!",
    "role": "admin"
}

def create_default_user():
    """
    Creates a default admin user if one does not already exist.
    """
    try:
        # Check if user already exists by trying to log in
        login_response = requests.post(f"{BASE_URL}/users/login", json={
            "email": USER_DATA["email"],
            "password": USER_DATA["password"]
        })

        if login_response.status_code == 200:
            logger.info(f"User '{USER_DATA['email']}' already exists. Skipping creation.")
            return

        # If login fails (user likely doesn't exist), create the user
        create_response = requests.post(f"{BASE_URL}/users/", json=USER_DATA)

        if create_response.status_code == 201:
            logger.info(f"Successfully created user: {USER_DATA['email']}")
        elif create_response.status_code == 400 and "already registered" in create_response.json().get("detail", ""):
             logger.info(f"User '{USER_DATA['email']}' already exists. Skipping creation.")
        else:
            logger.error(f"Failed to create user. Status: {create_response.status_code}, Response: {create_response.text}")

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Could not connect to the API at {BASE_URL}. Please ensure the backend server is running.")
        logger.error(e)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    create_default_user()
