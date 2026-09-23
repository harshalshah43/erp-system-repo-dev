from fastapi import FastAPI
from fastapi.responses import HTMLResponse,JSONResponse

from sqlalchemy import text
from pathlib import Path # Any future packages must be imported above this line
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent /"db"))
from connect import engine

app = FastAPI(title = "My ERP System")

@app.get("/home",response_class = HTMLResponse)
def home():
    return "<h1>Hello World</h1>"

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
