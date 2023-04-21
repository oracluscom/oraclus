from IPython import start_ipython
from app.main import app  # Replace this with the path to your FastAPI application instance

start_ipython(argv=[], user_ns=locals())
