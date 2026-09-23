import sys
from fastapi import FastAPI
from fastapi.responses import HTMLResponse,JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# db/ is a sibling folder, not an installed package, so put it on the
# import path before reusing the engine that connect.py already builds.
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "db"))
from connect import engine 

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

@app.get("/products-in-db")
def products_in_db():
    # return "<h1>Welcome to About Page</h1>"
    # return {'message':'Welcome to about page'}
    with engine.connect() as conn:
        query = "SELECT ProductID, ProductName, Price, stock_quantity, SupplierID FROM ecom.Product ORDER BY ProductID"
        rows = conn.execute(text(query)).mappings().all()
    return [dict(row) for row in rows]