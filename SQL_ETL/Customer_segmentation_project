-------------------
---- VIEW TABLE ---
--------------------
SELECT * FROM data;

SHOW COLUMNS FROM data; 
---------------------------------
-- CREATE A PROFITABLE CUSTOMERS TABLE BY ID --
----------------------------------
CREATE VIEW AS Profitable_Customer
SELECT
	 CustomerID, 
     sum(UnitPrice*Quantity) AS Total_Customers
FROM 
	data
Group BY
	CustomerID;
-------------------------------
-- Totla Quantitis by Country--
--------------------------------

-- 2. What is the total quantities sold per Country ? UK is the country with the Highest Quantities sold
SELECT Country, SUM(Quantity) AS quantities_sold
FROM data
Group BY Country; 

----------------------------------------
-- Total Sales & Quantities by Month -- 
---------------------------------------- 
/*
1. STEP 1: Update the existing table with ALTER FUNCTION TO ADD NEW EMPTY COLUMNS

 - Datetime  as type column
 - Month as type Integer
 - Year as type Integer 
 - Time as type Time 
*/ 

ALTER TABLE data
ADD COLUMN Date DATETIME,
ADD COLUMN Month INT,
ADD COLUMN Year INT,  
ADD COLUMN Time TIME;

---------------------------------------------------------
-- THIS ALLOWS FOR ROWS TO BE MODIFIED USING WHERE CLAUSE
---------------------------------------------------------
SET SQL_SAFE_UPDATES = 0;

/*
- STEP 2: From the InvoiceDate update the columns with the appropriate format using STRING TO DATE SQL function
*/
UPDATE data
SET Date = str_to_date(InvoiceDate, '%m/%d/%Y %H:%i'),
	Year =  YEAR(Date),
    Month = month(Date), 
    Time = time(Date);

/*STEP 3: ADD a Empty Month Name Column to allow Months that are stated as text as not Integer*/
 ALTER Table data 
 ADD COLUMN Month_Name text; 

/* STEP 4: Converting the Number Month to Full Month Name e.g 12 = December*/
 UPDATE data 
 SET Date = str_to_date(InvoiceDate, '%m/%d/%Y %H:%i'),
     Month_Name = monthname(Date);
     
 ----------------------------------------------------
 -- SHOW THE TABLES COLUMNS HAVE UPDATED -----------
 ---------------------------------------------------
SELECT InvoiceDate, date, Month, Year,time, Month_Name
FROM data;

-----------------------------------
-- CREATE A SALES BY MONTH TABLE --
-----------------------------------
-- Total Sales by Month, Units Price & Quantities Sold:
CREATE TABLE Totals_Month AS
SELECT 
	Month_Name,
   Sum(UnitPrice) AS Total_Unit_Price,
   Sum(UnitPrice * Quantity) AS Total_Sales,
   Sum(Quantity) AS Total_Quantities
FROM
	data
Group by 
	Month_Name;

----------------------------
-- TOTAL SALES TABLE --
---------------------------

CREATE TABLE Total_Sales_table AS
SELECT 
	SUM(Quantity) AS Total_Quantity, 
    SUM(Quantity * UnitPrice) AS Total_Sales, 
    Sum(UnitPrice) AS Total_Unit_Price
FROM 
	data
WHERE 
	CustomerID IS NOT NULL AND CustomerID <> '';

-- SELECT *
-- FROM Total_Sales_table;
/**/ -- total_sales_table
-- To check for unique outcomes in a column use/ DISTINCT

------------------------------------------
--  Total Price of ALL STOCK (BATCH STOCK)
------------------------------------------
CREATE TABLE BATCH_TABLE AS
SELECT
		CustomerID, 
		InvoiceNo,
        UnitPrice, 
        Quantity
FROM
	data; 

SELECT
	InvoiceNo,
	CustomerID,
    Quantity,
	SUM(UnitPrice * Quantity) AS Batch_Price
FROM
	data
GROUP BY
		InvoiceNo;
		
-- * FROM BATCH_TABLE;
-- invoiceNo,
  --  CustomerID,
  --  SUM(UnitPrice * Quantity) AS Batch_Price FROM
    -- data
-- GROUP BY InvoiceNo; 

-- SELECT * FROM BATCH_TABLE;


