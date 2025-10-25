"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field, constr
from typing import Optional, List
from datetime import datetime
from enum import Enum


# === Common ===
class ErrorCode(str, Enum):
    """Standard error codes."""
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: dict = Field(..., example={
        "code": "VALIDATION_ERROR",
        "message": "参数不合法",
        "details": {}
    })


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    total: int
    page: int
    pageSize: int


# === Auth ===
class LoginRequest(BaseModel):
    """Login request body."""
    email: EmailStr
    password: constr(min_length=6)


class RegisterRequest(BaseModel):
    """Register request body."""
    email: EmailStr
    password: constr(min_length=6)
    name: constr(min_length=1, max_length=50)


class AuthResponse(BaseModel):
    """Auth response with token."""
    token: str
    user: dict


class UserProfile(BaseModel):
    """User profile."""
    id: str
    name: str
    email: str
    avatar: Optional[str] = None


# === Favorites ===
class FavoriteType(str, Enum):
    """Favorite item type."""
    PAPER = "paper"
    KNOWLEDGE = "knowledge"


class CreateFavoriteRequest(BaseModel):
    """Create favorite request."""
    type: FavoriteType
    targetId: str
    tags: List[str] = []


class FavoriteItem(BaseModel):
    """Favorite item response."""
    id: str
    type: FavoriteType
    title: str
    description: Optional[str] = None
    author: Optional[str] = None
    date: str
    source: Optional[str] = None
    tags: List[str] = []


class FavoritesResponse(BaseModel):
    """Favorites list response."""
    total: int
    page: int
    pageSize: int
    items: List[FavoriteItem]


# === Notes ===
class CreateNoteRequest(BaseModel):
    """Create note request."""
    title: str
    content: Optional[str] = ""
    folder: Optional[str] = None
    tags: List[str] = []


class UpdateNoteRequest(BaseModel):
    """Update note request."""
    title: Optional[str] = None
    content: Optional[str] = None
    folder: Optional[str] = None
    tags: Optional[List[str]] = None


class NoteItem(BaseModel):
    """Note item response."""
    id: str
    title: str
    content: str
    folder: str
    tags: List[str]
    updatedAt: datetime
    createdAt: datetime


class NoteFolderItem(BaseModel):
    """Note folder item."""
    id: str
    name: str
    count: int


# === Knowledge Base (TODO) ===
class CreateKnowledgeBaseRequest(BaseModel):
    """Create knowledge base request."""
    name: str
    description: Optional[str] = ""
    tags: List[str] = []


# === Hub (TODO) ===
class HubItem(BaseModel):
    """Hub item for knowledge plaza."""
    id: str
    title: str
    desc: str
    icon: str
    subs: int
    contents: int

