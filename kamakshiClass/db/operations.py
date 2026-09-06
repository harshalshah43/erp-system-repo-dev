"""CRUD operations for the ecom schema (Suppliers, Product, Orders).

Every function opens a transaction with `engine.begin()`, so the work is
committed on success and rolled back automatically if the database raises
(check constraint, unique email, foreign key, ...).

Values are always passed as bound parameters (:name), never string
formatting -- that is what keeps SQL injection out and lets Postgres
handle types/quoting for us.
"""
#CRUD - Create, Read, Update, Delete

import pandas as pd
from sqlalchemy import text

from connect import engine

SCHEMA = "ecom"
TABLES = ("suppliers", "product", "orders")


def show(table):
    """Read -- return every row of `table` as a DataFrame."""
    if table.lower() not in TABLES:
        raise ValueError(f"Unknown table {table!r}, expected one of {TABLES}")
    return pd.read_sql(f"SELECT * FROM {SCHEMA}.{table}", engine)

#helper function as it has a _ prefix
def _write(sql, params, returning=False):
    """Run an INSERT/UPDATE/DELETE and return the new id or the row count."""
    with engine.begin() as conn:
        result = conn.execute(text(sql), params)
        if returning:
            row = result.fetchone()
            return row[0] if row else None
        return result.rowcount


#Suppliers
    #Insert
def insert_supplier(supplier_name, contact_email):
    """Add a supplier and return the generated SupplierID.

    Contact_email is UNIQUE, so a repeat email raises IntegrityError.
    """
    sql = f"""
        INSERT INTO {SCHEMA}.Suppliers (Supplier_Name, Contact_email)
        VALUES (:name, :email)
        RETURNING SupplierID
    """
    return _write(sql, {"name": supplier_name, "email": contact_email}, returning=True)


    #Update
def update_supplier(supplier_id, supplier_name=None, contact_email=None):
    """Update the fields that were passed in. Returns rows affected."""
    fields, params = [], {"id": supplier_id}

    if supplier_name is not None:
        fields.append("Supplier_Name = :name")
        params["name"] = supplier_name
    if contact_email is not None:
        fields.append("Contact_email = :email")
        params["email"] = contact_email

    if not fields:
        return 0

    sql = f"UPDATE {SCHEMA}.Suppliers SET {', '.join(fields)} WHERE SupplierID = :id"
    return _write(sql, params)


    #Delete
def delete_supplier(supplier_id):
    """Delete a supplier.

    FK_SupplierID is ON DELETE NO ACTION, so this fails while any product
    still points at the supplier -- delete those products first.
    """
    sql = f"DELETE FROM {SCHEMA}.Suppliers WHERE SupplierID = :id"
    return _write(sql, {"id": supplier_id})


#Orders
    #Insert
def insert_order(product_id, quantity_ordered, order_date=None):
    """Add an order and return the generated OrderID.

    order_date falls back to the CURRENT_DATE default when left as None.
    Quantity_ordered must be >= 1 (Chk_qty).
    """
    if order_date is None:
        sql = f"""
            INSERT INTO {SCHEMA}.Orders (ProductID, Quantity_ordered)
            VALUES (:product_id, :qty)
            RETURNING OrderID
        """
        params = {"product_id": product_id, "qty": quantity_ordered}
    else:
        sql = f"""
            INSERT INTO {SCHEMA}.Orders (ProductID, Order_Date, Quantity_ordered)
            VALUES (:product_id, :order_date, :qty)
            RETURNING OrderID
        """
        params = {
            "product_id": product_id,
            "order_date": order_date,
            "qty": quantity_ordered,
        }
    return _write(sql, params, returning=True)


    #Update
def update_order(order_id, product_id=None, quantity_ordered=None, order_date=None):
    """Update the fields that were passed in. Returns rows affected."""
    fields, params = [], {"id": order_id}

    if product_id is not None:
        fields.append("ProductID = :product_id")
        params["product_id"] = product_id
    if quantity_ordered is not None:
        fields.append("Quantity_ordered = :qty")
        params["qty"] = quantity_ordered
    if order_date is not None:
        fields.append("Order_Date = :order_date")
        params["order_date"] = order_date

    if not fields:
        return 0

    sql = f"UPDATE {SCHEMA}.Orders SET {', '.join(fields)} WHERE OrderID = :id"
    return _write(sql, params)


    #Delete
def delete_order(order_id):
    """Delete a single order. Returns rows affected."""
    sql = f"DELETE FROM {SCHEMA}.Orders WHERE OrderID = :id"
    return _write(sql, {"id": order_id})


#Products
    #Insert
def insert_product(product_name, price, stock_quantity, supplier_id):
    """Add a product and return the generated ProductID.

    Price must be > 0 (Chk_price) and stock_quantity >= 0 (Chk_Stockqty);
    supplier_id has to be an existing SupplierID.
    """
    sql = f"""
        INSERT INTO {SCHEMA}.Product (ProductName, Price, stock_quantity, SupplierID)
        VALUES (:name, :price, :qty, :supplier_id)
        RETURNING ProductID
    """
    params = {
        "name": product_name,
        "price": price,
        "qty": stock_quantity,
        "supplier_id": supplier_id,
    }
    return _write(sql, params, returning=True)


    #Update
def update_product(product_id, product_name=None, price=None,
                   stock_quantity=None, supplier_id=None):
    """Update the fields that were passed in. Returns rows affected."""
    fields, params = [], {"id": product_id}

    if product_name is not None:
        fields.append("ProductName = :name")
        params["name"] = product_name
    if price is not None:
        fields.append("Price = :price")
        params["price"] = price
    if stock_quantity is not None:
        fields.append("stock_quantity = :qty")
        params["qty"] = stock_quantity
    if supplier_id is not None:
        fields.append("SupplierID = :supplier_id")
        params["supplier_id"] = supplier_id

    if not fields:
        return 0

    sql = f"UPDATE {SCHEMA}.Product SET {', '.join(fields)} WHERE ProductID = :id"
    return _write(sql, params)


def change_stock(product_id, delta):
    """Add `delta` to stock_quantity -- pass a negative value to sell stock.

    Chk_Stockqty rejects the update if it would take stock below zero.
    """
    sql = f"""
        UPDATE {SCHEMA}.Product
        SET stock_quantity = stock_quantity + :delta
        WHERE ProductID = :id
    """
    return _write(sql, {"id": product_id, "delta": delta})


    #Delete
def delete_product(product_id):
    """Delete a product.

    The Orders FK is ON DELETE CASCADE, so that product's orders go too.
    """
    sql = f"DELETE FROM {SCHEMA}.Product WHERE ProductID = :id"
    return _write(sql, {"id": product_id})


if __name__ == "__main__":
    #Create
    supplier_id = insert_supplier("Test Supplier", "test.supplier@gmail.com")
    product_id = insert_product("Bonds", 2500, 40, supplier_id)
    order_id = insert_order(product_id, 5)
    print(f"Inserted supplier={supplier_id}, product={product_id}, order={order_id}")

    #Read
    print("\nSuppliers:\n", show("suppliers"))
    print("\nProduct:\n", show("product"))
    print("\nOrders:\n", show("orders"))

    #Update
    print("\nSupplier rows updated:", update_supplier(supplier_id, supplier_name="Test Supplier Ltd"))
    print("Product rows updated:", update_product(product_id, price=2750))
    print("Stock rows updated:", change_stock(product_id, -5))
    print("Order rows updated:", update_order(order_id, quantity_ordered=8))
    print("\nProduct after updates:\n", show("product"))

    #Delete -- order, then product, then supplier, to respect the foreign keys
    print("\nOrder rows deleted:", delete_order(order_id))
    print("Product rows deleted:", delete_product(product_id))
    print("Supplier rows deleted:", delete_supplier(supplier_id))
