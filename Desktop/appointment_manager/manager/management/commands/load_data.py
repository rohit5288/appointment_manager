import csv
from django.core.management import BaseCommand
from manager.models import Student


ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the child data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    help = "Loads data from csv"

    def handle(self, *args, **options):
        if Student.objects.exists():
            print('child data already loaded...exiting.')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return
            
        # Show this before loading the data into the database
        print("Loading childrens data")
        #Code to load the data into database
        for row in csv.DictReader(open('./students.csv')):
            student=Student(id=row['id'], first_name=row['first_name'],last_name=row['last_name'], ethinicity=row['ethnicity'],date_of_birth=row['date_of_birth'],gender=row['gender'])  
            student.save()
            