from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create a SQLite database engine
engine = create_engine('sqlite:///bank.db')


DBSession = sessionmaker(bind=engine)
