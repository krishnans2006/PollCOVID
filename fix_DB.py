from flask_sqlalchemy import SQLAlchemy

from main import db, Location

while True:
  try:
    print([value for value in db.engine.execute(raw_input("SQL Query: "))])
  except Exception as e:
    print(e)