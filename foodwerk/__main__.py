"""Package entry point.

Run from the project root:
    python -m foodwerk
"""

from dotenv import load_dotenv
load_dotenv()  # lädt .env automatisch, falls vorhanden

from .application import FoodWerkApplication

if __name__ == "__main__":
    FoodWerkApplication().run()
