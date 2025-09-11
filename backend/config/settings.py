from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# The root of the project is the 'backend' directory.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""
    GOOGLE_APPLICATION_CREDENTIALS: str
    PROJECT_ID: str
    # Use an alias to read from GOOGLE_CLOUD_LOCATION in the .env file if it exists
    LOCATION: str = Field(default="us-central1", alias="GOOGLE_CLOUD_LOCATION") # Example: "us-central1", "europe-west1"
    GEMINI_MODEL_NAME: str = "gemini-2.5-pro" # Changed back to gemini-2.5-pro based on user feedback

    # Configure Pydantic to load from a specific .env file path, making it independent of the current working directory
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, extra='ignore')

settings = Settings()

# --- IMPORTANT: Guide for .env file ---
# This block is for user guidance during setup.
# In a production environment, ensure these variables are set externally.
if not ENV_FILE_PATH.exists():
    print("\n--- Setup Warning ---")
    print(f"'.env' file not found at '{ENV_FILE_PATH}'.")
    print("Please create one in the 'backend' directory with the following content:")
    print("-----------------------------------------------------------------")
    print("GOOGLE_APPLICATION_CREDENTIALS=\"/path/to/your/service-account-key.json\"")
    print("PROJECT_ID=\"your-gcp-project-id\"")
    print("# The following can be set, but have defaults:")
    print("# GOOGLE_CLOUD_LOCATION=\"us-central1\"  <-- Note: this is read into the LOCATION setting")
    print("# GEMINI_MODEL_NAME=\"gemini-1.5-flash\"")
    print("-----------------------------------------------------------------\
")
