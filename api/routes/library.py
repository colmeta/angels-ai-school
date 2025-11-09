"""
Library Management API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from api.services.library import get_library_service


router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class BookAdd(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    category: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    copies: int = 1
    location: Optional[str] = None


class BookBorrow(BaseModel):
    student_id: str
    book_id: str
    due_date: str


# ============================================================================
# BOOK CATALOG
# ============================================================================

@router.post("/library/books/add")
async def add_book(school_id: str, data: BookAdd):
    """Add book to library catalog"""
    service = get_library_service(school_id)
    return service.add_book(
        title=data.title,
        author=data.author,
        isbn=data.isbn,
        category=data.category,
        publisher=data.publisher,
        publication_year=data.publication_year,
        copies=data.copies,
        location=data.location
    )


@router.get("/library/books/search")
async def search_books(
    school_id: str,
    search_term: Optional[str] = None,
    category: Optional[str] = None,
    available_only: bool = False
):
    """Search books in catalog"""
    service = get_library_service(school_id)
    return {
        "success": True,
        "books": service.search_books(search_term, category, available_only)
    }


@router.get("/library/books/{book_id}")
async def get_book(school_id: str, book_id: str):
    """Get book details"""
    service = get_library_service(school_id)
    book = service.get_book_by_id(book_id)
    
    if not book:
        return {"success": False, "error": "Book not found"}
    
    return {"success": True, "book": book}


@router.patch("/library/books/{book_id}/copies")
async def update_copies(school_id: str, book_id: str, new_total_copies: int):
    """Update total copies of a book"""
    service = get_library_service(school_id)
    return service.update_book_copies(book_id, new_total_copies)


# ============================================================================
# BORROWING SYSTEM
# ============================================================================

@router.post("/library/borrow")
async def borrow_book(school_id: str, data: BookBorrow):
    """Student borrows a book"""
    service = get_library_service(school_id)
    return service.borrow_book(
        student_id=data.student_id,
        book_id=data.book_id,
        due_date=data.due_date
    )


@router.patch("/library/return/{borrowing_id}")
async def return_book(school_id: str, borrowing_id: str):
    """Student returns a book"""
    service = get_library_service(school_id)
    return service.return_book(borrowing_id)


@router.patch("/library/fine/{borrowing_id}/pay")
async def pay_fine(school_id: str, borrowing_id: str):
    """Mark fine as paid"""
    service = get_library_service(school_id)
    return service.pay_fine(borrowing_id)


# ============================================================================
# QUERIES & REPORTS
# ============================================================================

@router.get("/library/student/{student_id}/borrowings")
async def get_student_borrowings(
    school_id: str,
    student_id: str,
    include_returned: bool = False
):
    """Get borrowing history for a student"""
    service = get_library_service(school_id)
    return {
        "success": True,
        "borrowings": service.get_student_borrowings(student_id, include_returned)
    }


@router.get("/library/overdue")
async def get_overdue_books(school_id: str):
    """Get all overdue books"""
    service = get_library_service(school_id)
    return {
        "success": True,
        "overdue_books": service.get_overdue_books()
    }


@router.get("/library/fines/unpaid")
async def get_unpaid_fines(school_id: str):
    """Get all unpaid library fines"""
    service = get_library_service(school_id)
    return {
        "success": True,
        "unpaid_fines": service.get_unpaid_fines()
    }


@router.get("/library/statistics")
async def get_library_statistics(school_id: str):
    """Get library statistics"""
    service = get_library_service(school_id)
    return service.get_library_statistics()
