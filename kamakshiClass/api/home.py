import sys
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from sqlalchemy import text

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent/"db"))

from connect import engine
app=FastAPI(title = "My ERP System")

@app.get("/",response_class=HTMLResponse)
def home():
    return "<h1>Hello World</h1>"


@app.get("/about",response_class=JSONResponse)
def about():
    return {'message':'welcome to about page'}


@app.get("/products",response_class=HTMLResponse)
def products():
    with engine.connect()as conn:
        query=  """
                Select * from ecom.Product Order By ProductID;
                """
        rows= conn.execute(text(query)).mappings().all()

        html="""
        <html>
            <head>
                <title>Products</title>
            </head>
            <body>
                <h1>Products</h1>
                <table border="1">
                    <th>Product ID</th>
                    <th>Product Name</th>
                    <th>Price</th>
                    <th>Stock Qty</th>
                    <th>Supplier ID</th>
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

@app.get("/orders",response_class=HTMLResponse)
def orders():
    with engine.connect()as conn:
        query=  """
                Select * from ecom.Orders Order By OrderID;
                """
        rows= conn.execute(text(query)).mappings().all()

        html="""
        <html>
            <head>
                <title>Orders</title>
            </head>
            <body>
                <h1>Orders</h1>
                <table border="1">
                    <th>Order ID</th>
                    <th>Product ID</th>
                    <th>Order Date</th>
                    <th>Quantity Ordered</th>
        """
        for row in rows:
            html += f"""
                    <tr>

                        <td>{row['orderid']}</td>
                        <td>{row['productid']}</td>
                        <td>{row['order_date']}</td>
                        <td>{row['quantity_ordered']}</td>

                    </tr>
                    """
        html += """    
                </table>
            </body>
        </html>
        """

        return html

@app.get("/suppliers",response_class=HTMLResponse)
def suppliers():
    with engine.connect()as conn:
        query=  """
                Select * from ecom.Suppliers Order By SupplierID;
                """
        rows= conn.execute(text(query)).mappings().all()

        html="""
        <html>
            <head>
                <title>Suppliers</title>
            </head>
            <body>
                <h1>Suppliers</h1>
                <table border="1">
                    <th>Supplier ID</th>
                    <th>SupplierName</th>
                    <th>Contact Email</th>
        """
        for row in rows:
            html += f"""
                    <tr>

                        <td>{row['supplierid']}</td>
                        <td>{row['supplier_name']}</td>
                        <td>{row['contact_email']}</td>

                    </tr>
                    """
        html += """    
                </table>
            </body>
        </html>
        """

        return html

