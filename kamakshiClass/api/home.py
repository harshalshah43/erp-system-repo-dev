import sys
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse

app=FastAPI(title = "My ERP System")

@app.get("/",response_class=HTMLResponse)
def home():
    return "<h1>Hello World</h1>"


@app.get("/about",response_class=JSONResponse)
def about():
    return {'message':'welcome to about page'}


@app.get("/products",response_class=JSONResponse)
def products():
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
