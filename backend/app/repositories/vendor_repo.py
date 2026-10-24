from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.vendor import Vendor
from app.models.invoice import Invoice

class VendorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, vendor_id: int) -> Optional[Vendor]:
        return self.db.execute(
            select(Vendor).where(Vendor.id == vendor_id)
        ).scalar_one_or_none()

    def get_by_gstin(self, gstin: str) -> Optional[Vendor]:
        if not gstin:
            return None
        return self.db.execute(
            select(Vendor).where(func.upper(Vendor.gstin) == gstin.strip().upper())
        ).scalar_one_or_none()

    def get_by_name(self, name: str) -> Optional[Vendor]:
        if not name:
            return None
        return self.db.execute(
            select(Vendor).where(func.lower(Vendor.name) == name.strip().lower())
        ).scalar_one_or_none()

    def find_or_create(
        self, 
        name: str, 
        gstin: Optional[str] = None, 
        address: Optional[str] = None,
        pan: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> Vendor:
        vendor = None
        if gstin:
            vendor = self.get_by_gstin(gstin)
        if not vendor and name:
            vendor = self.get_by_name(name)

        if vendor:
            # Update missing attributes
            if gstin and not vendor.gstin:
                vendor.gstin = gstin.strip().upper()
            if address and not vendor.address:
                vendor.address = address
            if pan and not vendor.pan:
                vendor.pan = pan
            if phone and not vendor.phone:
                vendor.phone = phone
            if email and not vendor.email:
                vendor.email = email
            self.db.add(vendor)
            self.db.commit()
            self.db.refresh(vendor)
            return vendor

        # Create new vendor
        new_vendor = Vendor(
            name=name.strip() if name else "Unknown Vendor",
            gstin=gstin.strip().upper() if gstin else None,
            address=address,
            pan=pan,
            phone=phone,
            email=email
        )
        self.db.add(new_vendor)
        self.db.commit()
        self.db.refresh(new_vendor)
        return new_vendor

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Vendor]:
        # Only list vendors that have active invoices in the system
        stmt = (
            select(Vendor)
            .join(Invoice, Invoice.vendor_id == Vendor.id)
            .group_by(Vendor.id)
            .order_by(Vendor.name.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())
