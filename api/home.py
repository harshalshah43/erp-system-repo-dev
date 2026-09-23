import sys
from fastapi import FastAPI
from fastapi.responses import HTMLResponse,JSONResponse

# import pandas as pd
# from sqlalchemy import create_engine

# username = "harshal"
# password = "testing101"
# port = "5432"
# db_name = "harshal"
# host="localhost"

# connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"

# engine = create_engine(connection_string)

app = FastAPI(title = "My ERP System")

@app.get("/home",response_class = HTMLResponse)
def home():
    return "<h1>Hello World</h1>"

@app.get("/about",response_class = JSONResponse)
def about(): 
    # return "<h1>Welcome to About Page</h1>"
    return {'message':'Welcome to about page'}

@app.get("/products",response_class = JSONResponse)
def products(): 
    # return "<h1>Welcome to About Page</h1>"
    return {
        "product1":{
            'name':"Pencil",
            'price':'400',
            'currency':'inr',
            'qty':20
        },
        "product2":{
            'name':"Pencil",
            'price':'400',
            'currency':'inr',
            'qty':20
        },
        "product3":{
            'name':"Pencil",
            'price':'400',
            'currency':'inr',
            'qty':20
        }
    }