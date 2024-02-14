from src.setup.create_database import create_new_database
from src.setup import fill_impacts_and_generation_types
from src.setup.fill_regions import fill_regions

if __name__ == '__main__':
    create_new_database()
    fill_regions()
    fill_impacts_and_generation_types.main()