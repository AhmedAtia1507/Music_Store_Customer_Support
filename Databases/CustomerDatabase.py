import sqlite3
import threading

class CustomerDatabase:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path="Customers.db"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path="Customers.db"):
        if not self._initialized:
            print("Initializing CustomerDatabase...")
            self.db_path = db_path
            self._initialized = True
            self._setup_database()

    def _setup_database(self):
        """Set up the database tables and sample data"""
        self.create_customers_table()
        self.create_invoices_table()
        self.populate_customers_sample_data()
        self.populate_invoices_sample_data()

    def _get_connection(self):
        """Get a new connection for the current thread"""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def create_customers_table(self):
        """Create a table to store customer data."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                   CREATE TABLE IF NOT EXISTS customers (
                       id TEXT PRIMARY KEY,
                       phone_number TEXT NOT NULL UNIQUE,
                       email TEXT NOT NULL UNIQUE
                   )
                   ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
    
    def create_invoices_table(self):
        """Create a table to store invoice data."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                   CREATE TABLE IF NOT EXISTS invoices (
                       id TEXT PRIMARY KEY,
                       customer_id TEXT NOT NULL,
                       amount REAL,
                       date TEXT NOT NULL,
                       employee_name TEXT NOT NULL DEFAULT 'System',
                       FOREIGN KEY(customer_id) REFERENCES customers(id)
                   )
                   ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating invoices table: {e}")

    def populate_customers_sample_data(self):
        """Populate the database with sample customer data."""
        sample_customers = [
            ("customer_1", "+55 (12) 3923-5555", "customer1@example.com"),
            ("customer_2", "+55 (21) 99876-5432", "customer2@example.com"),
            ("customer_3", "+55 (11) 91234-5678", "customer3@example.com")
        ]
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany("INSERT OR IGNORE INTO customers (id, phone_number, email) VALUES (?, ?, ?)", sample_customers)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error populating sample data: {e}")

    def populate_invoices_sample_data(self):
        """Populate the database with sample invoice data."""
        sample_invoices = [
            ("invoice_1", "customer_1", 150.75, "2023-10-01", "Alice"),
            ("invoice_2", "customer_2", 200.00, "2023-10-05", "Bob"),
            ("invoice_3", "customer_3", 75.50, "2023-10-08", "Charlie"),
            ("invoice_4", "customer_1", 50.25, "2023-10-10", "Alice")
        ]
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany("INSERT INTO invoices (id,customer_id, amount, date, employee_name) VALUES (?, ?, ?, ?, ?)", sample_invoices)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error populating invoice sample data: {e}")
    
    def check_customer_exists(self, customer_id: str = None, phone_number: str = None, email: str = None) -> bool:
        """Check if a customer exists based on customer_id, phone_number, or email."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT 1 FROM customers WHERE "
                conditions = []
                params = []
                
                if customer_id:
                    conditions.append("id = ?")
                    params.append(customer_id)
                if phone_number:
                    conditions.append("phone_number = ?")
                    params.append(phone_number)
                if email:
                    conditions.append("email = ?")
                    params.append(email)
                
                if not conditions:
                    return False
                
                query += " OR ".join(conditions)
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result is not None
                
        except sqlite3.Error as e:
            print(f"Error checking user existence: {e}")
            return False
    
    def get_customer_details(self, customer_id: str = None, phone_number: str = None, email: str = None) -> dict:
        """Retrieve customer details based on customer_id, phone_number, or email."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM customers WHERE "
                conditions = []
                params = []
                
                if customer_id:
                    conditions.append("id = ?")
                    params.append(customer_id)
                if phone_number:
                    conditions.append("phone_number = ?")
                    params.append(phone_number)
                if email:
                    conditions.append("email = ?")
                    params.append(email)
                
                if not conditions:
                    return {}
                
                query += " OR ".join(conditions)
                cursor.execute(query, params)
                row = cursor.fetchone()
                
                if row:
                    return {"customer_id": row[0], "phone_number": row[1], "email": row[2]}
                    
        except sqlite3.Error as e:
            print(f"Error retrieving customer details: {e}")

        return {}

    def get_invoices_by_customer_sorted_by_date(self, customer_id: str) -> list[dict]:
        """
        Retrieve all invoices for a specific customer sorted by date in descending order.
        Args:
            customer_id (str): The unique identifier of the customer
        Returns:
            list[dict]: A list of dictionaries containing invoice data with keys:
                       - invoice_id: The unique invoice identifier
                       - customer_id: The customer's unique identifier
                       - amount: The invoice amount
                       - date: The invoice date
                       - employee_name: The name of the employee who created the invoice
                       Returns empty list if no invoices found or if an error occurs.
        Raises:
            sqlite3.Error: Database connection or query execution errors are caught
                          and logged, returning an empty list instead of raising.
        """
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM invoices WHERE customer_id = ? ORDER BY date DESC", (customer_id,))
                rows = cursor.fetchall()
                return [{"invoice_id": row[0], "customer_id": row[1], "amount": row[2], "date": row[3], "employee_name": row[4]} for row in rows]
                
        except sqlite3.Error as e:
            print(f"Error retrieving invoices: {e}")
            return []
    
    def get_invoices_sorted_by_unit_price(self, customer_id: str) -> list[dict]:
        """
        Retrieve all invoices for a specific customer sorted by amount in descending order.
        Args:
            customer_id (str): The unique identifier of the customer whose invoices to retrieve.
        Returns:
            list[dict]: A list of dictionaries containing invoice information with keys:
                       - invoice_id: The unique identifier of the invoice
                       - customer_id: The customer's unique identifier
                       - amount: The invoice amount
                       - date: The invoice date
                       - employee_name: The name of the employee who processed the invoice
                       Returns an empty list if no invoices are found or if an error occurs.
        Raises:
            sqlite3.Error: Database connection or query execution errors are caught and logged.
        Note:
            Despite the method name suggesting sorting by unit price, this method actually
            sorts invoices by the total amount field in descending order.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM invoices WHERE customer_id = ? ORDER BY amount DESC", (customer_id,))
                rows = cursor.fetchall()
                return [{"invoice_id": row[0], "customer_id": row[1], "amount": row[2], "date": row[3], "employee_name": row[4]} for row in rows]
                
        except sqlite3.Error as e:
            print(f"Error retrieving invoices: {e}")
            return []
    
    def get_employee_name_by_invoice_and_customer_id(self, invoice_id: str, customer_id: str) -> str:
        """
        Retrieves the employee name associated with a specific invoice and customer.
        Args:
            invoice_id (str): The unique identifier of the invoice
            customer_id (str): The unique identifier of the customer
        Returns:
            str: The name of the employee associated with the invoice, or empty string if not found
        Raises:
            sqlite3.Error: If there's an error executing the database query
        Example:
            >>> employee_name = db.get_employee_name_by_invoice_and_customer_id("INV001", "CUST123")
            >>> print(employee_name)
            "John Smith"
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT employee_name FROM invoices WHERE id = ? AND customer_id = ?", (invoice_id, customer_id))
                row = cursor.fetchone()
                return row[0] if row else ""
                
        except sqlite3.Error as e:
            print(f"Error retrieving employee name: {e}")
            return ""
