from sqlalchemy.orm import Session
from app.models.scan import Scan


def save_scan(db: Session, contract_name, contract_code, risk_score, risk_level, findings_json):
    scan = Scan(
        contract_name=contract_name,
        contract_code=contract_code,
        risk_score=risk_score,
        risk_level=risk_level,
        findings_json=findings_json,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def list_scans(db: Session, limit: int = 20):
    return (
        db.query(Scan)
        .order_by(Scan.created_at.desc())
        .limit(limit)
        .all()
    )


def get_scan(db: Session, scan_id: int):
    return db.query(Scan).filter(Scan.id == scan_id).first()


def delete_scan(db: Session, scan_id: int):
    scan = get_scan(db, scan_id)
    if scan:
        db.delete(scan)
        db.commit()
    return scan