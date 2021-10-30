import secrets
from sqlalchemy import create_engine

con = f"mysql+pymysql://{secrets.dbuser}:{secrets.dbpass}@{secrets.dbhost}/{secrets.dbname}"
print(con)
engine = create_engine(con)
print(engine.table_names())