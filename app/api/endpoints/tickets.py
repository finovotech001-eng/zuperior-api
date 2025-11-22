from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from app.core.database import get_db
from app.api.deps import get_current_active_user, require_role
from app.schemas.schemas import (
    TicketResponse,
    TicketCreate,
    TicketUpdate,
    TicketReplyResponse,
    TicketReplyCreate,
    TicketReplyUpdate,
    PaginatedResponse,
    MessageResponse
)
from app.crud.crud import ticket_crud, ticket_reply_crud
from app.models.models import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    order: str = Query("desc", regex="^(asc|desc)$"),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    ticket_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    List tickets for current user with pagination and filtering
    Admins can see all tickets, users can only see their own
    """
    filters: Dict[str, Any] = {}
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority
    if ticket_type:
        filters["ticketType"] = ticket_type
    
    # Admins can see all tickets, users only their own
    user_id = None if current_user.role == "admin" else current_user.id
    
    result = ticket_crud.get_multi(
        db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
        filters=filters,
        search=search,
        search_fields=["title", "description", "ticketNo"],
        user_id=user_id
    )
    
    # Convert SQLAlchemy objects to Pydantic models
    result['items'] = [TicketResponse.model_validate(item) for item in result['items']]
    
    return result


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get ticket by ID
    """
    ticket = ticket_crud.get_by_id(db, id=ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Users can only access their own tickets, admins can access all
    if current_user.role != "admin" and ticket.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this ticket"
        )
    
    return ticket


@router.get("/{ticket_id}/replies", response_model=List[TicketReplyResponse])
def get_ticket_replies(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all replies for a ticket
    """
    ticket = ticket_crud.get_by_id(db, id=ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Users can only access their own tickets, admins can access all
    if current_user.role != "admin" and ticket.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this ticket"
        )
    
    replies = ticket_reply_crud.get_by_ticket_id(db, ticket_id=ticket_id)
    
    # Filter out internal replies for non-admin users
    if current_user.role != "admin":
        replies = [reply for reply in replies if not reply.isInternal]
    
    return [TicketReplyResponse.model_validate(reply) for reply in replies]


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new ticket
    """
    ticket = ticket_crud.create(
        db,
        obj_in=ticket_in,
        userId=current_user.id
    )
    return ticket


@router.post("/{ticket_id}/replies", response_model=TicketReplyResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_reply(
    ticket_id: int,
    reply_in: TicketReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create reply to a ticket
    """
    ticket = ticket_crud.get_by_id(db, id=ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Users can only reply to their own tickets, admins can reply to any
    if current_user.role != "admin" and ticket.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reply to this ticket"
        )
    
    # Set sender name if not provided
    sender_name = reply_in.senderName if reply_in.senderName else (current_user.name or current_user.email)
    
    # Set sender type based on user role
    sender_type = "admin" if current_user.role == "admin" else "user"
    
    reply = ticket_reply_crud.create(
        db,
        obj_in=reply_in,
        ticketId=ticket_id,
        userId=current_user.id,
        senderName=sender_name,
        senderType=sender_type
    )
    
    return reply


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update ticket
    Users can only update their own tickets, admins can update any ticket
    """
    ticket = ticket_crud.get_by_id(db, id=ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Users can only update their own tickets, admins can update any
    if current_user.role != "admin" and ticket.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this ticket"
        )
    
    # Non-admin users can only update certain fields
    if current_user.role != "admin":
        update_data = ticket_update.model_dump(exclude_unset=True) if hasattr(ticket_update, 'model_dump') else ticket_update.dict(exclude_unset=True)
        # Remove admin-only fields
        update_data.pop('status', None)
        update_data.pop('assignedTo', None)
        ticket_update = TicketUpdate(**update_data)
    
    updated_ticket = ticket_crud.update(db, db_obj=ticket, obj_in=ticket_update)
    return updated_ticket


@router.put("/{ticket_id}/close", response_model=TicketResponse)
def close_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Close a ticket
    Users can close their own tickets, admins can close any ticket
    """
    ticket = ticket_crud.get_by_id(db, id=ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Users can only close their own tickets, admins can close any
    if current_user.role != "admin" and ticket.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to close this ticket"
        )
    
    closed_ticket = ticket_crud.close_ticket(
        db,
        ticket_id=ticket_id,
        closed_by=current_user.id
    )
    
    return closed_ticket


@router.put("/{ticket_id}/replies/{reply_id}", response_model=TicketReplyResponse)
def update_ticket_reply(
    ticket_id: int,
    reply_id: int,
    reply_update: TicketReplyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update ticket reply
    Users can only update their own replies, admins can update any reply
    """
    ticket = ticket_crud.get_by_id(db, id=ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    reply = ticket_reply_crud.get_by_id(db, id=reply_id)
    
    if not reply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply not found"
        )
    
    if reply.ticketId != ticket_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reply does not belong to this ticket"
        )
    
    # Users can only update their own replies, admins can update any
    if current_user.role != "admin" and reply.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this reply"
        )
    
    updated_reply = ticket_reply_crud.update(db, db_obj=reply, obj_in=reply_update)
    return updated_reply


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete ticket (admin only)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete tickets"
        )
    
    ticket = ticket_crud.get_by_id(db, id=ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    ticket_crud.delete(db, id=ticket_id)
    return None


@router.delete("/{ticket_id}/replies/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket_reply(
    ticket_id: int,
    reply_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete ticket reply
    Users can only delete their own replies, admins can delete any reply
    """
    ticket = ticket_crud.get_by_id(db, id=ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    reply = ticket_reply_crud.get_by_id(db, id=reply_id)
    
    if not reply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply not found"
        )
    
    if reply.ticketId != ticket_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reply does not belong to this ticket"
        )
    
    # Users can only delete their own replies, admins can delete any
    if current_user.role != "admin" and reply.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this reply"
        )
    
    ticket_reply_crud.delete(db, id=reply_id)
    return None

