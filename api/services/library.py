"""
Library Management Service
Book catalog, borrowing system, fines, library analytics
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from api.services.database import get_db_manager


class LibraryService:
    """Service for library management"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    # ============================================================================
    # BOOK CATALOG
    # ============================================================================
    
    def add_book(
        self,
        title: str,
        author: str,
        isbn: Optional[str] = None,
        category: Optional[str] = None,
        publisher: Optional[str] = None,
        publication_year: Optional[int] = None,
        copies: int = 1,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add book to library catalog"""
        query = """
        INSERT INTO library_books (
            school_id, title, author, isbn, category, publisher,
            publication_year, total_copies, available_copies, location
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, title, author, isbn, category, publisher,
             publication_year, copies, copies, location),
            fetch=True
        )
        
        return {
            "success": True,
            "book_id": result[0]['id'],
            "title": title,
            "copies": copies
        }
    
    def search_books(
        self,
        search_term: Optional[str] = None,
        category: Optional[str] = None,
        available_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Search books in catalog"""
        query = """
        SELECT 
            id,
            title,
            author,
            isbn,
            category,
            publisher,
            publication_year,
            total_copies,
            available_copies,
            location,
            status
        FROM library_books
        WHERE school_id = %s
        """
        
        params = [self.school_id]
        
        if search_term:
            query += " AND (title ILIKE %s OR author ILIKE %s OR isbn ILIKE %s)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if available_only:
            query += " AND available_copies > 0 AND status = 'available'"
        
        query += " ORDER BY title"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    def get_book_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Get book details"""
        query = """
        SELECT 
            id,
            title,
            author,
            isbn,
            category,
            publisher,
            publication_year,
            total_copies,
            available_copies,
            location,
            status
        FROM library_books
        WHERE id = %s
        """
        
        result = self.db.execute_query(query, (book_id,), fetch=True)
        return result[0] if result else None
    
    def update_book_copies(
        self,
        book_id: str,
        new_total_copies: int
    ) -> Dict[str, Any]:
        """Update total copies (when acquiring more copies)"""
        query = """
        UPDATE library_books
        SET total_copies = %s,
            available_copies = available_copies + (%s - total_copies),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND school_id = %s
        """
        
        self.db.execute_query(query, (new_total_copies, new_total_copies, book_id, self.school_id))
        
        return {
            "success": True,
            "book_id": book_id,
            "new_total_copies": new_total_copies
        }
    
    # ============================================================================
    # BORROWING SYSTEM
    # ============================================================================
    
    def borrow_book(
        self,
        student_id: str,
        book_id: str,
        due_date: str
    ) -> Dict[str, Any]:
        """Student borrows a book"""
        # Check availability
        book = self.get_book_by_id(book_id)
        
        if not book:
            return {"success": False, "error": "Book not found"}
        
        if book['available_copies'] <= 0:
            return {"success": False, "error": "No copies available"}
        
        # Check if student has overdue books
        overdue_query = """
        SELECT COUNT(*) as count
        FROM library_borrowings
        WHERE student_id = %s
        AND return_date IS NULL
        AND due_date < CURRENT_DATE
        """
        overdue = self.db.execute_query(overdue_query, (student_id,), fetch=True)
        
        if overdue and overdue[0]['count'] > 0:
            return {"success": False, "error": "Student has overdue books. Cannot borrow."}
        
        # Create borrowing record
        borrow_query = """
        INSERT INTO library_borrowings (
            school_id, student_id, book_id, borrowed_date, due_date
        ) VALUES (%s, %s, %s, CURRENT_DATE, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            borrow_query,
            (self.school_id, student_id, book_id, due_date),
            fetch=True
        )
        
        # Update available copies
        update_query = """
        UPDATE library_books
        SET available_copies = available_copies - 1
        WHERE id = %s
        """
        
        self.db.execute_query(update_query, (book_id,))
        
        return {
            "success": True,
            "borrowing_id": result[0]['id'],
            "student_id": student_id,
            "book_id": book_id,
            "due_date": due_date
        }
    
    def return_book(
        self,
        borrowing_id: str
    ) -> Dict[str, Any]:
        """Student returns a book"""
        # Get borrowing record
        get_query = """
        SELECT 
            book_id,
            student_id,
            due_date,
            return_date
        FROM library_borrowings
        WHERE id = %s
        """
        
        borrowing = self.db.execute_query(get_query, (borrowing_id,), fetch=True)
        
        if not borrowing:
            return {"success": False, "error": "Borrowing record not found"}
        
        if borrowing[0]['return_date'] is not None:
            return {"success": False, "error": "Book already returned"}
        
        # Calculate fine if overdue
        due_date = borrowing[0]['due_date']
        return_date = datetime.now().date()
        fine_amount = 0
        
        if return_date > due_date:
            # Get fine rules
            fine_query = """
            SELECT fine_per_day
            FROM library_fine_rules
            WHERE school_id = %s
            LIMIT 1
            """
            fine_rules = self.db.execute_query(fine_query, (self.school_id,), fetch=True)
            
            if fine_rules:
                fine_per_day = float(fine_rules[0]['fine_per_day'])
                days_overdue = (return_date - due_date).days
                fine_amount = fine_per_day * days_overdue
        
        # Update borrowing record
        return_query = """
        UPDATE library_borrowings
        SET return_date = CURRENT_DATE,
            fine_amount = %s,
            fine_paid = false
        WHERE id = %s
        """
        
        self.db.execute_query(return_query, (fine_amount, borrowing_id))
        
        # Update available copies
        book_id = borrowing[0]['book_id']
        update_query = """
        UPDATE library_books
        SET available_copies = available_copies + 1
        WHERE id = %s
        """
        
        self.db.execute_query(update_query, (book_id,))
        
        return {
            "success": True,
            "borrowing_id": borrowing_id,
            "fine_amount": fine_amount,
            "message": "Book returned" + (f" with fine: {fine_amount} UGX" if fine_amount > 0 else "")
        }
    
    def pay_fine(self, borrowing_id: str) -> Dict[str, Any]:
        """Mark fine as paid"""
        query = """
        UPDATE library_borrowings
        SET fine_paid = true
        WHERE id = %s
        """
        
        self.db.execute_query(query, (borrowing_id,))
        
        return {
            "success": True,
            "borrowing_id": borrowing_id
        }
    
    # ============================================================================
    # QUERIES & REPORTS
    # ============================================================================
    
    def get_student_borrowings(
        self,
        student_id: str,
        include_returned: bool = False
    ) -> List[Dict[str, Any]]:
        """Get borrowing history for a student"""
        query = """
        SELECT 
            lb.id,
            lb.borrowed_date,
            lb.due_date,
            lb.return_date,
            lb.fine_amount,
            lb.fine_paid,
            b.title,
            b.author,
            b.isbn
        FROM library_borrowings lb
        JOIN library_books b ON b.id = lb.book_id
        WHERE lb.student_id = %s
        """
        
        if not include_returned:
            query += " AND lb.return_date IS NULL"
        
        query += " ORDER BY lb.borrowed_date DESC"
        
        return self.db.execute_query(query, (student_id,), fetch=True)
    
    def get_overdue_books(self) -> List[Dict[str, Any]]:
        """Get all overdue books"""
        query = """
        SELECT 
            lb.id,
            lb.borrowed_date,
            lb.due_date,
            s.id as student_id,
            s.first_name,
            s.last_name,
            s.class_name,
            b.title,
            b.author,
            CURRENT_DATE - lb.due_date as days_overdue
        FROM library_borrowings lb
        JOIN students s ON s.id = lb.student_id
        JOIN library_books b ON b.id = lb.book_id
        WHERE lb.school_id = %s
        AND lb.return_date IS NULL
        AND lb.due_date < CURRENT_DATE
        ORDER BY days_overdue DESC
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)
    
    def get_unpaid_fines(self) -> List[Dict[str, Any]]:
        """Get all unpaid library fines"""
        query = """
        SELECT 
            lb.id,
            lb.fine_amount,
            s.id as student_id,
            s.first_name,
            s.last_name,
            s.class_name,
            b.title
        FROM library_borrowings lb
        JOIN students s ON s.id = lb.student_id
        JOIN library_books b ON b.id = lb.book_id
        WHERE lb.school_id = %s
        AND lb.fine_amount > 0
        AND lb.fine_paid = false
        ORDER BY lb.fine_amount DESC
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)
    
    def get_library_statistics(self) -> Dict[str, Any]:
        """Get library statistics"""
        # Total books
        books_query = """
        SELECT 
            COUNT(*) as total_titles,
            SUM(total_copies) as total_books,
            SUM(available_copies) as available_books
        FROM library_books
        WHERE school_id = %s
        """
        books = self.db.execute_query(books_query, (self.school_id,), fetch=True)
        
        # Currently borrowed
        borrowed_query = """
        SELECT COUNT(*) as count
        FROM library_borrowings
        WHERE school_id = %s AND return_date IS NULL
        """
        borrowed = self.db.execute_query(borrowed_query, (self.school_id,), fetch=True)
        
        # Overdue
        overdue_query = """
        SELECT COUNT(*) as count
        FROM library_borrowings
        WHERE school_id = %s
        AND return_date IS NULL
        AND due_date < CURRENT_DATE
        """
        overdue = self.db.execute_query(overdue_query, (self.school_id,), fetch=True)
        
        return {
            "success": True,
            "total_titles": books[0]['total_titles'] if books else 0,
            "total_books": books[0]['total_books'] if books else 0,
            "available_books": books[0]['available_books'] if books else 0,
            "currently_borrowed": borrowed[0]['count'] if borrowed else 0,
            "overdue_books": overdue[0]['count'] if overdue else 0
        }


def get_library_service(school_id: str) -> LibraryService:
    """Helper to get library service instance"""
    return LibraryService(school_id)
