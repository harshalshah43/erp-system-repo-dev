-- Connect to the right database first (run separately, not as part of the script):
-- \c your_database_name

-- Optional: create and use the ecom schema
CREATE SCHEMA IF NOT EXISTS ecom;
SET search_path TO ecom;

------------------------**** Task 1 and 2 ****------------------------
--** SUPPLIER TABLE
CREATE TABLE Suppliers
(
    SupplierID INTEGER GENERATED ALWAYS AS IDENTITY,
    Supplier_Name VARCHAR(100) NOT NULL,
    Contact_email VARCHAR(100) NOT NULL,
    CONSTRAINT PK_SupplierID PRIMARY KEY(SupplierID),
    CONSTRAINT UNI_EMAIL UNIQUE(Contact_email)
);

INSERT INTO Suppliers(Supplier_Name, Contact_email)
VALUES ('Kamakshi', 'kamakshi@gmail.com'),
       ('Shivam', 'shivam@gmail.com'),
       ('Yash', 'yash@gmail.com');

SELECT * FROM Suppliers;

--** Product TABLE
CREATE TABLE Product
(
    ProductID INTEGER GENERATED ALWAYS AS IDENTITY,
    ProductName VARCHAR(100) NOT NULL,
    Price DECIMAL(10,2),
    stock_quantity INTEGER DEFAULT 0,
    SupplierID INTEGER NOT NULL,
    CONSTRAINT PK_ProductID PRIMARY KEY(ProductID),
    CONSTRAINT FK_SupplierID FOREIGN KEY(SupplierID) REFERENCES Suppliers(SupplierID)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION,
    CONSTRAINT Chk_price CHECK(Price > 0),
    CONSTRAINT Chk_Stockqty CHECK(stock_quantity >= 0)
);

INSERT INTO Product(ProductName, Price, stock_quantity, SupplierID)
VALUES ('Mutual Funds', 500, 50, 1),
       ('Stocks', 1000, 20, 2),
       ('IPO', 10000, 100, 3),
       ('SIP', 3000, 80, 1);

SELECT * FROM Product;

--** Orders
CREATE TABLE Orders
(
    OrderID INTEGER GENERATED ALWAYS AS IDENTITY,
    ProductID INTEGER NOT NULL,
    Order_Date DATE DEFAULT CURRENT_DATE,
    Quantity_ordered INTEGER NOT NULL,
    CONSTRAINT PK_OrderID PRIMARY KEY(OrderID),
    CONSTRAINT Chk_qty CHECK(Quantity_ordered >= 1),
    FOREIGN KEY(ProductID) REFERENCES Product(ProductID)
        ON DELETE CASCADE
);

INSERT INTO Orders(ProductID, Quantity_ordered)
VALUES (2, 200), (1, 100), (3, 50), (4, 150);

SELECT * FROM Orders;

------------------------**** Task 3 ****------------------------

--1. Check Constraint Test: negative stock
INSERT INTO Product(ProductName, Price, stock_quantity, SupplierID)
VALUES ('IMP', 30, -2, 1);

-- Expected PostgreSQL error:
-- ERROR:  new row for relation "product" violates check constraint "chk_stockqty"
-- DETAIL:  Failing row contains (5, IMP, 30.00, -2, 1).

--2. Unique Constraint Test: duplicate email
INSERT INTO Suppliers(Supplier_Name, Contact_email)
VALUES ('Kakshi', 'kamakshi@gmail.com');

-- Expected PostgreSQL error:
-- ERROR:  duplicate key value violates unique constraint "uni_email"
-- DETAIL:  Key (contact_email)=(kamakshi@gmail.com) already exists.

--3. Foreign Key Restrict Test: delete supplier with linked products
DELETE FROM Suppliers WHERE SupplierID = 1;

-- Expected PostgreSQL error:
-- ERROR:  update or delete on table "suppliers" violates foreign key constraint "fk_supplierid" on table "product"
-- DETAIL:  Key (supplierid)=(1) is still referenced from table "product".

--4. Foreign Key Cascade Test: delete a product, verify cascade on orders
DELETE FROM Product WHERE ProductID = 1;
SELECT * FROM Orders;

-- Expected output: orders for ProductID 1 are gone,
-- remaining rows for ProductID 2, 3, 4 stay intact.

SELECT * FROM Product;
SELECT * FROM Suppliers;
SELECT * FROM Orders;