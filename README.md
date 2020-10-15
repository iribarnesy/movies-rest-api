# Movies Rest API

Author : Sylvain Iribarne

Exercice : Create a rest API with FastAPI & SQLAlchemy. Consumed with a jupyter notebook

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies.

```bash
pip install fastapi
pip install uvicorn
pip install pymysql
```

## Usage

### Launch the API server (with uvicorn)

To launch the server you have to execute the following command 

```bash
uvicorn main:app --reload
```

### Consume the API

You can consume the API from any http client, your navigator for example  : http://localhost:8000/movies

Example for the GET /movies/ route in Python :

```python
import pandas as pd
API_URL = "http://localhost:8000"
limit = 100
skip = 0
dfMovies = pd.read_json(API_URL+f"movies/?limit={limit}&skip={skip}")
```
## Doc

The full documentation of the API is accessible at http://localhost:8000/docs (tryable) or http://localhost:8000/redoc (prettier)