"""FastAPI front door for the ecom schema.

Run it from the erp-system/api folder:

    uvicorn home:app --reload

Then open http://127.0.0.1:8000 -- the three buttons there call the
three JSON endpoints below. Interactive docs: http://127.0.0.1:8000/docs
"""

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# db/ is a sibling folder, not an installed package, so put it on the
# import path before reusing the engine that connect.py already builds.
sys.path.append(str(Path(__file__).resolve().parent.parent / "db"))
from connect import engine  # noqa: E402

app = FastAPI(title="ERP System API", description="Suppliers, Products and Orders")

# Whitelist: the browser never chooses a table name, it picks one of these
# keys. That is what keeps a crafted URL from reaching arbitrary SQL.
TABLES = {
    "suppliers": "SELECT SupplierID, Supplier_Name, Contact_email FROM ecom.Suppliers ORDER BY SupplierID",
    "products": "SELECT ProductID, ProductName, Price, stock_quantity, SupplierID FROM ecom.Product ORDER BY ProductID",
    "orders": "SELECT OrderID, ProductID, Order_Date, Quantity_ordered FROM ecom.Orders ORDER BY OrderID",
}


def fetch_all(name):
    """Run the whitelisted query for `name` and return a list of dicts."""
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(TABLES[name])).mappings().all()
    except SQLAlchemyError as exc:
        # Container down, wrong password, missing schema... report it as a
        # 503 instead of leaking a stack trace to the browser.
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}")

    return [dict(row) for row in rows]


@app.get("/suppliers")
def get_suppliers():
    """Every supplier."""
    return fetch_all("suppliers")


@app.get("/products")
def get_products():
    """Every product."""
    return fetch_all("products")


@app.get("/orders")
def get_orders():
    """Every order."""
    return fetch_all("orders")


@app.get("/", response_class=HTMLResponse)
def home():
    """Landing page with one button per table."""
    return HTML_PAGE


HTML_PAGE = """
<title>ERP System</title>
<style>
  body { font-family: system-ui, sans-serif; margin: 2rem; }
  button { font-size: 1rem; padding: .5rem 1.2rem; margin-right: .5rem; cursor: pointer; }
  button.active { background: #1a1a1a; color: #fff; }
  table { border-collapse: collapse; margin-top: 1.5rem; }
  th, td { border: 1px solid #ccc; padding: .4rem .8rem; text-align: left; }
  th { background: #f2f2f2; }
  #msg { margin-top: 1.5rem; color: #b00; }
</style>

<h1>ERP System</h1>
<button onclick="load('products', this)">Products</button>
<button onclick="load('suppliers', this)">Suppliers</button>
<button onclick="load('orders', this)">Orders</button>

<div id="msg"></div>
<div id="out"></div>

<script>
async function load(name, btn) {
  document.querySelectorAll('button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('msg').textContent = 'Loading...';
  document.getElementById('out').innerHTML = '';

  const res = await fetch('/' + name);
  const data = await res.json();

  if (!res.ok) {                       // the 503 from fetch_all lands here
    document.getElementById('msg').textContent = data.detail || 'Request failed';
    return;
  }
  if (data.length === 0) {
    document.getElementById('msg').textContent = 'No rows in ' + name + '.';
    return;
  }

  document.getElementById('msg').textContent = '';
  const cols = Object.keys(data[0]);
  const head = '<tr>' + cols.map(c => '<th>' + c + '</th>').join('') + '</tr>';
  const body = data.map(r =>
    '<tr>' + cols.map(c => '<td>' + (r[c] ?? '') + '</td>').join('') + '</tr>'
  ).join('');
  document.getElementById('out').innerHTML = '<table>' + head + body + '</table>';
}
</script>
"""
