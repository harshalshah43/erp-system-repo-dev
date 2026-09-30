from datetime import date
from pydantic import EmailStr
import sys
from fastapi import FastAPI,Request,Form,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent/"db"))

from connect import engine
from operations import insert_product
from operations import insert_order
from operations import insert_supplier

app=FastAPI(title = "My ERP System")
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")


@app.get("/home",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(
        request,
        name= "home.html"
    )

@app.get("/products",response_class=HTMLResponse)
def products(request:Request):
    with engine.connect()as conn:
        query=  """
                Select * from ecom.Product Order By ProductID;
                """
        rows= conn.execute(text(query)).mappings().all()
        return templates.TemplateResponse(
           request,
           name = "products.html",
           context={
               "products":rows
           }
        )


@app.get("/orders",response_class=HTMLResponse)
def orders(request:Request):
    with engine.connect()as conn:
        query=  """
                Select * from ecom.Orders Order By OrderID;
                """
        rows= conn.execute(text(query)).mappings().all()

        return templates.TemplateResponse(
           request,
           name = "orders.html",
           context= {
               "orders":rows
           }
        )

@app.get("/suppliers",response_class=HTMLResponse)
def suppliers(request:Request):
    with engine.connect()as conn:
        query=  """
                Select * from ecom.Suppliers Order By SupplierID;
                """
        rows= conn.execute(text(query)).mappings().all()

        return templates.TemplateResponse(
           request,
           name = "suppliers.html",
           context= {
               "suppliers":rows
           }
        )

@app.get("/products/add",response_class = HTMLResponse)
def product_form(request:Request):
    return templates.TemplateResponse(
        request,
        'product_form.html',
        context = {

        }
    )

@app.post("/products/add", response_class=HTMLResponse)
def product_add(
    request: Request,
    product_name: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    supplier_id: int = Form(...),
):
    try:
        new_id = insert_product(
            product_name=product_name,
            price=price,
            stock_quantity=stock_quantity,
            supplier_id=supplier_id,
        )
        return f"""<h1>Product added successfully! (ID: {new_id})</h1>
               <a href="/products"><button type="button">Products</button></a>
        """
    except Exception as e:
        return templates.TemplateResponse(
            request,
            "product_form.html",
            {"error": str(e)}
        )

#edit product
@app.get("/products/edit/{productid}",response_class = HTMLResponse)
def product_edit_form(request:Request,productid: int):
    with engine.connect() as con:
        query="""
        Select * from ecom.Product where ProductID = :id
        """
        row = con.execute(text(query),{"id":productid})
        row = row.fetchone()
        print(row)
        if row is None:
            raise HTTPException(status_code = 404,detail="Product not found")
        
    return templates.TemplateResponse(
        request,
        'product_form.html',
        context = {
            'product':row
        }
    )

@app.get("/orders/add",response_class = HTMLResponse)
def orders_form(request:Request):
    return templates.TemplateResponse(
        request,
        'orders_form.html',
        context = {

        }
    )

@app.post("/orders/add", response_class=HTMLResponse)
def orders_add(
    request: Request,
    productid: int = Form(...),
    order_date: date = Form(...),
    quantity_ordered: int = Form(...),
):
    try:
        new_id = insert_order(
            productid=productid,
            order_date=order_date,
            quantity_ordered=quantity_ordered,
        )
        return f"""<h1>Order added successfully! (ID: {new_id})</h1>
               <a href="/orders"><button type="button">Orders</button></a>
        """
    except Exception as e:
        print("ORDER INSERT ERROR:", e)
        return templates.TemplateResponse(
            request,
            "orders_form.html",
            {"error": str(e)}
        )


@app.get("/suppliers/add",response_class = HTMLResponse)
def suppliers_form(request:Request):
    return templates.TemplateResponse(
        request,
        'suppliers_form.html',
        context = {

        }
    )

@app.post("/suppliers/add", response_class=HTMLResponse)
def supplier_add(
    request: Request,
    supplier_name: str = Form(...),
    contact_email: EmailStr = Form(...),
):
    try:
        new_id = insert_supplier(
            supplier_name=supplier_name,
            contact_email=contact_email,
        )
        return f"""<h1>Supplier added successfully! (ID: {new_id})</h1>
               <a href="/suppliers"><button type="button">Suppliers</button></a>
        """
    except Exception as e:
        print("Supplier INSERT ERROR:", e)
        return templates.TemplateResponse(
            request,
            "suppliers_form.html",
            {"error": str(e)}
        )

# @app.get("/suppliers/deleteconfirm",response_class = HTMLResponse)
# def suppliers_delete_confirmation(request:Request):
#     return templates.TemplateResponse(
#         request,
#         'suppliers_deleteconfirm.html',
#         context = {

#         }
#     )