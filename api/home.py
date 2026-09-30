from fastapi import FastAPI,Request,Form
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import text
from pathlib import Path # Any future packages must be imported above this line
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent /"db"))
from connect import engine
from operations import insert_product


app = FastAPI(title = "My ERP System")
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

@app.get("/home",response_class = HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(
        request,
        name = "home.html"
    )

@app.get("/about",response_class = JSONResponse)
def about(): 
    # return "<h1>Welcome to About Page</h1>"
    return {'message':'Welcome to about page'}

@app.get("/products",response_class = HTMLResponse)
def products(): 
    # return "<h1>Welcome to About Page</h1>"
    with engine.connect() as conn:
        query = """
                select * from ecom.Product order by ProductID;
                """
        rows = conn.execute(text(query)).mappings().all()
        
        html = """
        <html>
            <head>
                <title>Products</title>
            </head>
            <body>
                <h1>Products</h1>
                <table border = "1">
                    <tr>
                        <th>ProductID</th>
                        <th>Product Name</th>
                        <th>Price</th>
                        <th>Stock Qty</th>
                        <th>Supplier ID</th>
                    </tr>
        """

        for row in rows:
            html += f"""
                    <tr>
                        <td>{row['productid']}</td>
                        <td>{row['productname']}</td>
                        <td>{row['price']}</td>
                        <td>{row['stock_quantity']}</td>
                        <td>{row['supplierid']}</td>
                    </tr>
                    """

        html += """           
                </table>
            </body>
        </html>
        """

        return html

@app.get("/product/add",response_class = HTMLResponse)
def product_form(request:Request):
    return templates.TemplateResponse(
        request,
        'product_form.html',
        context = {

        }
    ) 

@app.post("/product/add", response_class=HTMLResponse)
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
                <a href = "products/"><button type = 'button'>Products</button></a>
                """
    except Exception as e:
        return templates.TemplateResponse(
            request,
            "product_form.html",
            {"error": str(e)}
        )

@app.get("/orders",response_class = HTMLResponse)
def orders(request:Request): 
    # return "<h1>Welcome to About Page</h1>"
    with engine.connect() as conn:
        query = """
                select * from ecom.Orders order by OrderID;
                """
        rows = conn.execute(text(query)).mappings().all()

        return templates.TemplateResponse(
            request,
            name = "orders.html",
            context = {
                'orders':rows
            }
        )

