"""Package entry point.

Run from the project root:
    python -m foodwerk
"""

from .application import FoodWerkApplication

if __name__ == "__main__":
    FoodWerkApplication().run()
