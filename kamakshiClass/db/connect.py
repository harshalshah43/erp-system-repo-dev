import pandas as pd
from sqlalchemy import create_engine


username = "kamakshi"
password = "kamshi"
port = "5432"
db_name = "postgres"
host="localhost"   # "postgres" (the compose service name) only resolves inside the Docker network


connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"

engine = create_engine(connection_string)
if engine:
    print("Connection established...")
    df1 = pd.read_sql('select * from ecom.suppliers',engine)
    df2 = pd.read_sql('select * from ecom.orders',engine)
    df3 = pd.read_sql('select * from ecom.product',engine)
    print(df1)
    print(df2)
    print(df3)
else:
    print("Sorry! Could not create connection...")