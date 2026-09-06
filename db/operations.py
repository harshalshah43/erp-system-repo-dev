"""CRUD operations for the ecom schema (Suppliers, Product, Orders).

Every function opens a transaction with `engine.begin()`, so the work is
committed on success and rolled back automatically if the database raises
(check constraint, unique email, foreign key, ...).

Values are always passed as bound parameters (:name), never string
formatting -- that is what keeps SQL injection out and lets Postgres
handle types/quoting for us.
"""

from sqlalchemy import text

from connect import engine


# ---------------------------------------------------------------- helpers

def show(table):
    """Print every row of ecom.<table>. Handy while testing."""
    with engine.connect() as conn:
        rows = conn.execute(text(f"SELECT * FROM ecom.{table}")).mappings().all()

    print(f"\n--- {table} ({len(rows)} rows) ---")
    for row in rows:
        print(dict(row))
    return rows


# ---------------------------------------------------------------- Suppliers

# Insert Suppliers
def insert_supplier(supplier_name, contact_email):
    """Add a supplier. Returns the new SupplierID.

    Fails on a duplicate email (constraint UNI_EMAIL).
    """
    sql = text("""
        INSERT INTO ecom.Suppliers (Supplier_Name, Contact_email)
        VALUES (:name, :email)
        RETURNING SupplierID
    """)
    with engine.begin() as conn:
        new_id = conn.execute(sql, {"name": supplier_name, "email": contact_email}).scalar_one()

    print(f"Inserted supplier {new_id}: {supplier_name}")
    return new_id


# Update Suppliers
def update_supplier(supplier_id, supplier_name=None, contact_email=None):
    """Update the name and/or the email of one supplier.

    COALESCE(:param, column) keeps the existing value when the argument
    is left as None, so one statement covers all the combinations.
    """
    sql = text("""
        UPDATE ecom.Suppliers
        SET Supplier_Name = COALESCE(:name, Supplier_Name),
            Contact_email = COALESCE(:email, Contact_email)
        WHERE SupplierID = :id
    """)
    with engine.begin() as conn:
        count = conn.execute(
            sql, {"id": supplier_id, "name": supplier_name, "email": contact_email}
        ).rowcount

    print(f"Updated {count} supplier(s) with id {supplier_id}")
    return count


# Delete Suppliers
def delete_supplier(supplier_id):
    """Delete a supplier.

    The FK on Product is ON DELETE NO ACTION, so a supplier that still has
    products cannot be deleted -- Postgres raises and the transaction rolls
    back. Delete or re-point those products first.
    """
    sql = text("DELETE FROM ecom.Suppliers WHERE SupplierID = :id")
    with engine.begin() as conn:
        count = conn.execute(sql, {"id": supplier_id}).rowcount

    print(f"Deleted {count} supplier(s) with id {supplier_id}")
    return count


# ---------------------------------------------------------------- Product

# Insert Product
def insert_product(product_name, price, stock_quantity, supplier_id):
    """Add a product. Returns the new ProductID.

    Price must be > 0 and stock_quantity >= 0 (Chk_price, Chk_Stockqty),
    and supplier_id must already exist in Suppliers.
    """
    sql = text("""
        INSERT INTO ecom.Product (ProductName, Price, stock_quantity, SupplierID)
        VALUES (:name, :price, :stock, :supplier_id)
        RETURNING ProductID
    """)
    with engine.begin() as conn:
        new_id = conn.execute(sql, {
            "name": product_name,
            "price": price,
            "stock": stock_quantity,
            "supplier_id": supplier_id,
        }).scalar_one()

    print(f"Inserted product {new_id}: {product_name}")
    return new_id


# Update Product
def update_product(product_id, product_name=None, price=None,
                   stock_quantity=None, supplier_id=None):
    """Update any subset of a product's columns."""
    sql = text("""
        UPDATE ecom.Product
        SET ProductName    = COALESCE(:name, ProductName),
            Price          = COALESCE(:price, Price),
            stock_quantity = COALESCE(:stock, stock_quantity),
            SupplierID     = COALESCE(:supplier_id, SupplierID)
        WHERE ProductID = :id
    """)
    with engine.begin() as conn:
        count = conn.execute(sql, {
            "id": product_id,
            "name": product_name,
            "price": price,
            "stock": stock_quantity,
            "supplier_id": supplier_id,
        }).rowcount

    print(f"Updated {count} product(s) with id {product_id}")
    return count


def change_stock(product_id, delta):
    """Add `delta` to a product's stock (use a negative number to reduce it).

    Doing the arithmetic inside SQL means Postgres reads and writes the row
    in one statement, so two users cannot overwrite each other's change.
    Chk_Stockqty rejects the update if it would go below zero.
    """
    sql = text("""
        UPDATE ecom.Product
        SET stock_quantity = stock_quantity + :delta
        WHERE ProductID = :id
        RETURNING stock_quantity
    """)
    with engine.begin() as conn:
        stock = conn.execute(sql, {"id": product_id, "delta": delta}).scalar_one_or_none()

    print(f"Product {product_id} stock is now {stock}")
    return stock


# Delete Product
def delete_product(product_id):
    """Delete a product.

    The FK on Orders is ON DELETE CASCADE, so every order of this product
    disappears with it.
    """
    sql = text("DELETE FROM ecom.Product WHERE ProductID = :id")
    with engine.begin() as conn:
        count = conn.execute(sql, {"id": product_id}).rowcount

    print(f"Deleted {count} product(s) with id {product_id} (orders cascaded)")
    return count


# ---------------------------------------------------------------- Orders

# Insert Orders
def insert_order(product_id, quantity_ordered, order_date=None):
    """Place an order. Returns the new OrderID.

    quantity_ordered must be >= 1 (Chk_qty). Leaving order_date as None
    lets the DEFAULT CURRENT_DATE fill it in.
    """
    sql = text("""
        INSERT INTO ecom.Orders (ProductID, Quantity_ordered, Order_Date)
        VALUES (:product_id, :qty, COALESCE(:order_date, CURRENT_DATE))
        RETURNING OrderID
    """)
    with engine.begin() as conn:
        new_id = conn.execute(sql, {
            "product_id": product_id,
            "qty": quantity_ordered,
            "order_date": order_date,
        }).scalar_one()

    print(f"Inserted order {new_id} for product {product_id}")
    return new_id


# Update Orders
def update_order(order_id, product_id=None, quantity_ordered=None, order_date=None):
    """Update any subset of an order's columns."""
    sql = text("""
        UPDATE ecom.Orders
        SET ProductID        = COALESCE(:product_id, ProductID),
            Quantity_ordered = COALESCE(:qty, Quantity_ordered),
            Order_Date       = COALESCE(:order_date, Order_Date)
        WHERE OrderID = :id
    """)
    with engine.begin() as conn:
        count = conn.execute(sql, {
            "id": order_id,
            "product_id": product_id,
            "qty": quantity_ordered,
            "order_date": order_date,
        }).rowcount

    print(f"Updated {count} order(s) with id {order_id}")
    return count


# Delete Orders
def delete_order(order_id):
    """Delete a single order. Nothing else references Orders, so this is safe."""
    sql = text("DELETE FROM ecom.Orders WHERE OrderID = :id")
    with engine.begin() as conn:
        count = conn.execute(sql, {"id": order_id}).rowcount

    print(f"Deleted {count} order(s) with id {order_id}")
    return count


# ---------------------------------------------------------------- demo

if __name__ == "__main__":
    # A small end-to-end run against the container. Everything it creates,
    # it deletes again, so the table contents are unchanged afterwards.
    supplier_id = insert_supplier("Test Supplier", "test.supplier@example.com")
    update_supplier(supplier_id, contact_email="updated.supplier@example.com")

    product_id = insert_product("Test Bond", 250, 10, supplier_id)
    change_stock(product_id, -3)

    order_id = insert_order(product_id, 5)
    update_order(order_id, quantity_ordered=7)

    show("orders")

    delete_order(order_id)
    delete_product(product_id)     # would cascade the order anyway
    delete_supplier(supplier_id)   # only works now that its product is gone
