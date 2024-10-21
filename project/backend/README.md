# Running Project on your local

This API is about to learn simple backend API development with Python. It covers the following
- ORM
- Python Web Framework(Decided to use Tornado Web)
- ORM migrations & usage

## Dependencies installation
go to backend folder
```
pip install -r requirements.txt
```

# Running Migrations

## adding new migration after modifying the model

```
alembic revision --autogenerate -m "init script"
```
## Migrate to latest head
```
alembic upgrade head
```

## Downgrade to initial migration
```
alembic downgrade base
```

## Running Seeds

Go to backend folder
```
python seed.py
```

## Things todo
- To add test cases pytest
- Test Coverage
- To add Postgres DB 
