# Make it work
python3.9 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
deactevate
source ./venv/bin/activate

# run postgres in docker
./pg_docker.sh

# upgrade db
alembic upgrade head

# run tests
pytest -vv

# reset db and run app
alembic downgrade base && alembic upgrade head
python -m app.main