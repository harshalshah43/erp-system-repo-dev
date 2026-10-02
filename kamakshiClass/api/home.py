from datetime import date
from pydantic import EmailStr
import sys
from fastapi import FastAPI,Request,Form,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent/"db"))

from connect import engine
from operations import insert_product,update_product,delete_product
from operations import insert_order,update_order,delete_order
from operations import insert_supplier,update_supplier,delete_supplier

app=FastAPI(title = "My ERP System")
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

#show only the database's own message, not the full SQL statement
def error_message(e):
    return str(getattr(e, "orig", e))

#HOME
@app.get("/home",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(
        request,
        name= "home.html"
    )

#GET PRODUCT TABLE
@app.get("/products",response_class=HTMLResponse)
def products(request:Request, deleted: int = None):
    with engine.connect()as conn:
        query=  """
                Select * from ecom.Product Order By ProductID;
                """
        rows= conn.execute(text(query)).mappings().all()
        return templates.TemplateResponse(
           request,
           name = "products.html",
           context={
               "products":rows,
               "deleted": deleted
           }        
           
        )

#GET ORDERS TABLE
@app.get("/orders",response_class=HTMLResponse)
def orders(request:Request, deleted: int = None):
    with engine.connect()as conn:
        query=  """
                Select * from ecom.Orders Order By OrderID;
                """
        rows= conn.execute(text(query)).mappings().all()

        return templates.TemplateResponse(
           request,
           name = "orders.html",
           context= {
               "orders":rows,
               "deleted": deleted
           }
        )

#GET SUPPLIERS TABLE
@app.get("/suppliers",response_class=HTMLResponse)
def suppliers(request:Request, deleted: int = None, delete_failed: int = None):
    with engine.connect()as conn:
        query=  """
                Select * from ecom.Suppliers Order By SupplierID;
                """
        rows= conn.execute(text(query)).mappings().all()

        return templates.TemplateResponse(
           request,
           name = "suppliers.html",
           context= {
               "suppliers":rows,
               "deleted": deleted,
               "delete_failed": delete_failed
           }
        )

#ADD NEW PRODUCT - GET AND POST
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
            {
                "error": error_message(e),
                "product": {
                    "productname": product_name,
                    "price": price,
                    "stock_quantity": stock_quantity,
                    "supplierid": supplier_id,
                },
            }
        )

#EDIT PRODUCT - GET AND POST
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

@app.post("/products/edit/{productid}", response_class=HTMLResponse)
def product_edit(
    request: Request,
    productid: int,
    product_name: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    supplier_id: int = Form(...),
):
    try:
        update_product(
            productid=productid,
            product_name=product_name,
            price=price,
            stock_quantity=stock_quantity,
            supplier_id=supplier_id,
        )
        return RedirectResponse(url="/products", status_code=303)
    except Exception as e:
        print("PRODUCT UPDATE ERROR:", e)
        return templates.TemplateResponse(
            request,
            "product_form.html",
            {
                "error": error_message(e),
                "product": {
                    "productid": productid,
                    "productname": product_name,
                    "price": price,
                    "stock_quantity": stock_quantity,
                    "supplierid": supplier_id,
                },
            }
        )


#DELETE PRODUCT
@app.post("/products/delete/{productid}")
def product_delete(productid: int):
    delete_product(productid)
    return RedirectResponse(url=f"/products?deleted={productid}", status_code=303)



#ADD NEW ORDER - GET AND POST
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
            {
                "error": error_message(e),
                "order": {
                    "productid": productid,
                    "order_date": order_date,
                    "quantity_ordered": quantity_ordered,
                },
            }
        )

#EDIT ORDER - GET AND POST
@app.get("/orders/edit/{orderid}",response_class = HTMLResponse)
def orders_edit_form(request:Request,orderid: int):
    with engine.connect() as con:
        query="""
        Select * from ecom.Orders where OrderID = :id
        """
        print("QUERY:",query)
        row = con.execute(text(query),{"id":orderid})
        row = row.fetchone()
        print(row)
        if row is None:
            raise HTTPException(status_code = 404,detail="Order not found")
        
    return templates.TemplateResponse(
        request,
        'orders_form.html',
        context = {
            'order':row
        }
    )

@app.post("/orders/edit/{orderid}", response_class=HTMLResponse)
def orders_edit(
    request: Request,
    orderid: int,
    productid: int = Form(...),
    order_date: date = Form(...),
    quantity_ordered: int = Form(...),
):
    try:
        update_order(
            order_id=orderid,
            productid=productid,
            order_date=order_date,
            quantity_ordered=quantity_ordered,
        )
        return RedirectResponse(url="/orders", status_code=303)
    except Exception as e:
        print("ORDER UPDATE ERROR:", e)
        return templates.TemplateResponse(
            request,
            "orders_form.html",
            {
                "error": error_message(e),
                "order": {
                    "orderid": orderid,
                    "productid": productid,
                    "order_date": order_date,
                    "quantity_ordered": quantity_ordered,
                },
            }
        )


#DELETE ORDER
@app.post("/orders/delete/{orderid}")
def order_delete(orderid: int):
    delete_order(orderid)
    return RedirectResponse(url=f"/orders?deleted={orderid}", status_code=303)


#ADD NEW SUPPLIER - GET AND POST
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
            {
                "error": error_message(e),
                "supplier": {
                    "supplier_name": supplier_name,
                    "contact_email": contact_email,
                },
            }
        )


#EDIT SUPPLIERS - GET AND POST
@app.get("/suppliers/edit/{supplierid}",response_class = HTMLResponse)
def suppliers_edit_form(request:Request,supplierid: int):
    with engine.connect() as con:
        query="""
        Select * from ecom.Suppliers where SupplierID = :id
        """
        print("QUERY:",query)
        row = con.execute(text(query),{"id":supplierid})
        row = row.fetchone()
        print(row)
        if row is None:
            raise HTTPException(status_code = 404,detail="Supplier not found")
        
    return templates.TemplateResponse(
        request,
        'suppliers_form.html',
        context = {
            'supplier':row
        }
    )

@app.post("/suppliers/edit/{supplierid}", response_class=HTMLResponse)
def suppliers_edit(
    request: Request,
    supplierid: int,
    supplier_name: str = Form(...),
    contact_email: EmailStr = Form(...),
):
    try:
        update_supplier(
            supplierid=supplierid,
            supplier_name=supplier_name,
            contact_email=contact_email,
        )
        return RedirectResponse(url="/suppliers", status_code=303)
    except Exception as e:
        print("SUPPLIER UPDATE ERROR:", e)
        return templates.TemplateResponse(
            request,
            "suppliers_form.html",
            {
                "error": error_message(e),
                "supplier": {
                    "supplierid": supplierid,
                    "supplier_name": supplier_name,
                    "contact_email": contact_email,
                },
            }
        )

#DELETE SUPPLIER
@app.post("/suppliers/delete/{supplierid}")
def supplier_delete(supplierid: int):
    try:
        delete_supplier(supplierid)
    except IntegrityError as e:
        print("SUPPLIER DELETE ERROR:", e)
        return RedirectResponse(url=f"/suppliers?delete_failed={supplierid}", status_code=303)
    return RedirectResponse(url=f"/suppliers?deleted={supplierid}", status_code=303)