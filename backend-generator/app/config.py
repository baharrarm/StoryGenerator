from dotenv import load_dotenv; load_dotenv()
import os

# read from env (works on EC2, Docker, and locally)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # fallback for local dev
    "postgresql+psycopg2://app:app@localhost:5432/appdb"
)