from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.schemas import (
    NotificationResponse,
    NotificationCreate,
    NotificationUpdate,
    PaginatedResponse,
    MessageResponse
)
from app.crud.crud import notification_crud
from app.models.models import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    order: str = Query("desc", regex="^(asc|desc)$"),
    is_read: Optional[bool] = Query(None),
    type: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    List notifications for current user with pagination and filtering
    """
    filters: Dict[str, Any] = {}
    if is_read is not None:
        filters["isRead"] = is_read
    if type:
        filters["type"] = type
    
    result = notification_crud.get_multi(
        db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
        filters=filters,
        search=search,
        search_fields=["title", "message"],
        user_id=current_user.id
    )
    
    # Convert SQLAlchemy objects to Pydantic models
    result['items'] = [NotificationResponse.model_validate(item) for item in result['items']]
    
    return result


@router.get("/unread-count", response_model=Dict[str, int])
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get count of unread notifications for current user
    """
    from sqlalchemy import func
    from app.models.models import Notification
    
    count = db.query(func.count(Notification.id)).filter(
        Notification.userId == current_user.id,
        Notification.isRead == False
    ).scalar()
    
    return {"unread_count": count or 0}


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get notification by ID
    """
    notification = notification_crud.get_by_id(db, id=notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    if notification.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this notification"
        )
    
    return notification


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    notification_in: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new notification (typically used by system/admin)
    """
    notification = notification_crud.create(db, obj_in=notification_in, userId=current_user.id)
    return notification


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: str,
    notification_update: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update notification (typically to mark as read)
    """
    notification = notification_crud.get_by_id(db, id=notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    if notification.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this notification"
        )
    
    updated_notification = notification_crud.update(db, db_obj=notification, obj_in=notification_update)
    return updated_notification


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark notification as read
    """
    notification = notification_crud.get_by_id(db, id=notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    if notification.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this notification"
        )
    
    updated_notification = notification_crud.mark_as_read(db, notification_id=notification_id)
    return updated_notification


@router.put("/mark-all-read", response_model=MessageResponse)
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark all notifications as read for current user
    """
    count = notification_crud.mark_all_as_read(db, user_id=current_user.id)
    return {"message": f"Marked {count} notifications as read"}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete notification
    """
    notification = notification_crud.get_by_id(db, id=notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    if notification.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this notification"
        )
    
    notification_crud.delete(db, id=notification_id)
    return None

