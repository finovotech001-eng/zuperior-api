from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_active_admin
from app.schemas.schemas import (
    CountryResponse,
    CountryCreate,
    CountryUpdate,
    PaginatedResponse
)
from app.crud.crud import country_crud
from app.models.models import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_countries(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    order: str = Query("asc", regex="^(asc|desc)$"),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None)
):
    """
    List countries with pagination
    """
    filters = {}
    if is_active is not None:
        filters["isActive"] = is_active
        
    result = country_crud.get_multi(
        db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
        filters=filters,
        search=search,
        search_fields=["name", "code"]
    )
    
    # Convert SQLAlchemy objects to Pydantic models
    result['items'] = [CountryResponse.model_validate(item) for item in result['items']]
    
    return result


@router.get("/{country_id}", response_model=CountryResponse)
def get_country(
    country_id: str,
    db: Session = Depends(get_db)
):
    """
    Get country by ID
    """
    country = country_crud.get_by_id(db, id=country_id)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    return country


@router.post("/", response_model=CountryResponse, status_code=status.HTTP_201_CREATED)
def create_country(
    country_in: CountryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Create new country (Admin only)
    """
    # Check if code already exists
    existing = country_crud.get_by_code(db, code=country_in.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Country code already exists"
        )
    
    country = country_crud.create(db, obj_in=country_in)
    return country


@router.put("/{country_id}", response_model=CountryResponse)
def update_country(
    country_id: str,
    country_update: CountryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Update country (Admin only)
    """
    country = country_crud.get_by_id(db, id=country_id)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    
    updated_country = country_crud.update(db, db_obj=country, obj_in=country_update)
    return updated_country


@router.delete("/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(
    country_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Delete country (Admin only)
    """
    country = country_crud.get_by_id(db, id=country_id)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    
    country_crud.delete(db, id=country_id)
    return None
