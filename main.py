import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

# -----------------------------
# Configuration
# -----------------------------
PORT = int(os.getenv("PORT", "8000"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "bookshop-service")

# -----------------------------
# Logging Setup
# -----------------------------
logger = logging.getLogger(SERVICE_NAME)


# -----------------------------
# Models
# -----------------------------
class Book(BaseModel):
    id: int
    title: str
    author: str
    price: float
    stock: int


# In-memory database
BOOKS_DB: dict[int, Book] = {
    1: Book(
        id=1,
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        price=12.99,
        stock=45,
    ),
    2: Book(
        id=2,
        title="1984",
        author="George Orwell",
        price=14.99,
        stock=32,
    ),
    3: Book(
        id=3,
        title="To Kill a Mockingbird",
        author="Harper Lee",
        price=13.50,
        stock=28,
    ),
    4: Book(
        id=4,
        title="Pride and Prejudice",
        author="Jane Austen",
        price=11.99,
        stock=52,
    ),
    5: Book(
        id=5,
        title="The Catcher in the Rye",
        author="J.D. Salinger",
        price=12.50,
        stock=19,
    ),
}


# -----------------------------
# FastAPI app
# -----------------------------
@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("📚 Bookshop service starting up")
    logger.info(f"Loaded {len(BOOKS_DB)} books into catalog")
    yield
    logger.info("📚 Bookshop service shutting down")


app = FastAPI(title="Bookshop Service", lifespan=lifespan)

logging.info(f"🚀 Service {SERVICE_NAME} running on port {PORT}")


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {"status": "ok", "service": SERVICE_NAME, "version": "1.0.0"}


@app.get("/health")
def health():
    logger.info("Health check endpoint called")
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/books")
def list_books(author: Optional[str] = None, min_price: Optional[float] = None):
    logger.info(f"Listing books - filters: author={author}, min_price={min_price}")
    books = list(BOOKS_DB.values())
    if author:
        books = [b for b in books if author.lower() in b.author.lower()]
    if min_price:
        books = [b for b in books if b.price >= min_price]
    logger.info(f"Retrieved {len(books)} books from database")
    return {"books": books}


@app.get("/books/{book_id}")
def get_book(book_id: int):
    logger.info(f"Fetching book with ID: {book_id}")
    book = BOOKS_DB[book_id]
    logger.info(f"Retrieved book: {book['title']} by {book['author']}")
    return {"book": book}
