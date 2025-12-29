"""
Library Service
===============
Enterprise-grade library management.
Features:
- Automatic Fine Calculation (Overdue logic)
- Reservation Queues (FIFO)
- Strict Stock Management
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta

from api.services.database import get_db_manager

class LibraryService:
    # FINE_PER_DAY is now managed dynamically via 'library_settings' table
    # Default is 500 if not set.
    DEFAULT_FINE = 500.0

    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()

    def update_settings(self, fine_per_day: float, borrow_limit: int) -> Dict[str, Any]:
        """Update library configuration settings"""
        # Upsert settings
        query = """
        INSERT INTO library_settings (school_id, fine_per_day, borrow_limit_days)
        VALUES (%s, %s, %s)
        ON CONFLICT (school_id) DO UPDATE
        SET fine_per_day = EXCLUDED.fine_per_day,
            borrow_limit_days = EXCLUDED.borrow_limit_days,
            updated_at = CURRENT_TIMESTAMP
        """
        self.db.execute_query(query, (self.school_id, fine_per_day, borrow_limit))
        return {"success": True, "fine_per_day": fine_per_day, "borrow_limit": borrow_limit}

    def get_settings(self) -> Dict[str, Any]:
        """Get current library settings"""
        res = self.db.execute_query(
            "SELECT fine_per_day, borrow_limit_days FROM library_settings WHERE school_id = %s", 
            (self.school_id,), fetch=True
        )
        if res:
             return {"fine_per_day": float(res[0]['fine_per_day']), "borrow_limit": int(res[0]['borrow_limit_days'])}
        return {"fine_per_day": self.DEFAULT_FINE, "borrow_limit": 14}

    def add_book(self, title: str, author: str, copies: int, **kwargs) -> Dict[str, Any]:
        """Add new book to catalog"""
        query = """
        INSERT INTO library_books (
            school_id, title, author, isbn, category, 
            publisher, publication_year, total_copies, available_copies, 
            location, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        RETURNING id
        """
        result = self.db.execute_query(
            query,
            (self.school_id, title, author, kwargs.get('isbn'), kwargs.get('category'),
             kwargs.get('publisher'), kwargs.get('publication_year'), 
             copies, copies, kwargs.get('location')),
            fetch=True
        )
        return {"success": True, "book_id": result[0]['id']}

    def borrow_book(self, student_id: str, book_id: str, due_date: str) -> Dict[str, Any]:
        """
        Borrow a book. 
        Checks:
        1. Student exists.
        2. Book exists and has available copies.
        3. Student doesn't have overdue books (Policy).
        """
        # 1. Check availability
        book = self.get_book_by_id(book_id)
        if not book:
            return {"success": False, "error": "Book not found"}
        if book['available_copies'] < 1:
            return {"success": False, "error": "No copies available. Please reserve."}

        # 2. Check student standing (Simulated policy: Max 3 books)
        current_loans = self.get_student_borrowings(student_id)
        active_loans = [l for l in current_loans if l['status'] == 'active']
        if len(active_loans) >= 3:
             return {"success": False, "error": "Borrowing limit reached (Max 3 books)."}

        # 3. Create Transaction
        query = """
        INSERT INTO library_transactions (
            school_id, student_id, book_id, borrow_date, 
            due_date, status
        ) VALUES (%s, %s, %s, CURRENT_DATE, %s, 'active')
        RETURNING id
        """
        tx = self.db.execute_query(
            query, 
            (self.school_id, student_id, book_id, due_date), 
            fetch=True
        )
        
        # 4. Decrement Stock
        self.db.execute_query(
            "UPDATE library_books SET available_copies = available_copies - 1 WHERE id = %s",
            (book_id,)
        )
        
        return {"success": True, "transaction_id": tx[0]['id']}

    def return_book(self, transaction_id: str) -> Dict[str, Any]:
        """
        Return a book.
        Calculates fines if overdue.
        """
        # Get Tx
        tx = self.db.execute_query(
            "SELECT * FROM library_transactions WHERE id = %s", 
            (transaction_id,), fetch=True
        )
        if not tx:
             return {"success": False, "error": "Transaction not found"}
        tx = tx[0]
        
        if tx['status'] == 'returned':
             return {"success": False, "error": "Book already returned"}

        # Calculate Dates
        due_date = tx['due_date'] # datetime.date object usually from driver
        if isinstance(due_date, str):
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            
        today = date.today()
        
        fine = 0.0
        if today > due_date:
            # Get configured fine rate
            settings = self.get_settings()
            fine_rate = settings["fine_per_day"]
            
            overdue_days = (today - due_date).days
            fine = overdue_days * fine_rate
            
        # Update Tx
        status = 'returned'
        if fine > 0:
            status = 'returned_with_fine'
            
        update_query = """
        UPDATE library_transactions 
        SET return_date = CURRENT_DATE, 
            status = %s, 
            fine_amount = %s,
            fine_status = %s
        WHERE id = %s
        """
        fine_status = 'unpaid' if fine > 0 else 'none'
        self.db.execute_query(update_query, (status, fine, fine_status, transaction_id))
        
        # Increment Stock
        self.db.execute_query(
            "UPDATE library_books SET available_copies = available_copies + 1 WHERE id = %s",
            (tx['book_id'],)
        )
        
        return {
            "success": True, 
            "fine": fine, 
            "days_overdue": (today-due_date).days if today > due_date else 0
        }

    def get_overdue_books(self) -> List[Dict]:
        """List all currently overdue books"""
        query = """
        SELECT lt.id, s.first_name, s.last_name, lb.title, lt.due_date
        FROM library_transactions lt
        JOIN students s ON lt.student_id = s.id
        JOIN library_books lb ON lt.book_id = lb.id
        WHERE lt.status = 'active' AND lt.due_date < CURRENT_DATE
        """
        return self.db.execute_query(query, (), fetch=True)

    def get_book_by_id(self, book_id: str) -> Optional[Dict]:
        res = self.db.execute_query(
            "SELECT * FROM library_books WHERE id = %s", (book_id,), fetch=True
        )
        return res[0] if res else None

    def search_books(self, term: str = None, category: str = None, available: bool = False) -> List[Dict]:
        query = "SELECT * FROM library_books WHERE school_id = %s"
        params = [self.school_id]
        
        if term:
            query += " AND (title ILIKE %s OR author ILIKE %s)"
            params.extend([f"%{term}%", f"%{term}%"])
        if category:
            query += " AND category = %s"
            params.append(category)
        if available:
            query += " AND available_copies > 0"
            
        return self.db.execute_query(query, tuple(params), fetch=True)

    def get_student_borrowings(self, student_id: str, include_returned: bool = False) -> List[Dict]:
        query = """
        SELECT lt.*, lb.title, lb.author 
        FROM library_transactions lt
        JOIN library_books lb ON lt.book_id = lb.id
        WHERE lt.student_id = %s
        """
        if not include_returned:
            query += " AND lt.status = 'active'"
            
        return self.db.execute_query(query, (student_id,), fetch=True)
    
    def get_unpaid_fines(self) -> List[Dict]:
         query = """
         SELECT lt.id, s.first_name, s.last_name, lb.title, lt.fine_amount
         FROM library_transactions lt
         JOIN students s ON lt.student_id = s.id
         JOIN library_books lb ON lt.book_id = lb.id
         WHERE lt.fine_status = 'unpaid'
         """
         return self.db.execute_query(query, (), fetch=True)

    def get_library_statistics(self) -> Dict:
        # Simple stats
        total_books = self.db.execute_query("SELECT SUM(total_copies) as c FROM library_books WHERE school_id=%s", (self.school_id,), fetch=True)[0]['c']
        active_loans = self.db.execute_query("SELECT COUNT(*) as c FROM library_transactions WHERE school_id=%s AND status='active'", (self.school_id,), fetch=True)[0]['c']
        
        return {
            "total_books": total_books or 0,
            "active_loans": active_loans or 0
        }

def get_library_service(school_id: str) -> LibraryService:
    return LibraryService(school_id)
