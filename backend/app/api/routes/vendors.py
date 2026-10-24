from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.vendor_repo import VendorRepository
from app.schemas.vendor import VendorResponse

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.get("", response_model=List[VendorResponse])
def list_vendors(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    repo = VendorRepository(db)
    return repo.list_all(limit=limit, offset=offset)

@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    repo = VendorRepository(db)
    vendor = repo.get_by_id(vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found"
        )
    return vendor
