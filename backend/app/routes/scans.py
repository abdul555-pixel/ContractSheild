from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.scan_repository import list_scans, get_scan, delete_scan

router = APIRouter(prefix="/scans", tags=["Scans"])

@router.get("/")
def get_all_scans(db: Session = Depends(get_db)):
    scans = list_scans(db)
    return [
        {
            "id": s.id,
            "contract_name": s.contract_name,
            "risk_level": s.risk_level,
            "risk_score": float(s.risk_score) if s.risk_score else None,
            "created_at": s.created_at,
        }
        for s in scans
    ]

@router.get("/{scan_id}")
def get_one_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {
        "id": scan.id,
        "contract_name": scan.contract_name,
        "contract_code": scan.contract_code,
        "risk_score": float(scan.risk_score) if scan.risk_score else None,
        "risk_level": scan.risk_level,
        "findings": scan.findings_json,
        "created_at": scan.created_at,
    }

@router.delete("/{scan_id}")
def remove_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = delete_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"deleted": True, "id": scan_id}