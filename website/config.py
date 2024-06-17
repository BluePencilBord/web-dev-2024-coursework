from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

SECRET_KEY = os.environ['SECRET_KEY']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_USER = os.environ['DB_USER']
DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['DB_NAME']
DB_PORT = os.environ['DB_PORT']