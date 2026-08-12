from app.db.database import SessionLocal
from app.models.scan import Scan


def save_scan(
    contract_code: str,
    findings: list,
    risk_score: float,
) -> int:

    db = SessionLocal()

    try:
        scan = Scan(
            contract_code=contract_code,
            total_findings=len(findings),
            overall_risk=risk_score,
            findings_json=findings,
        )

        db.add(scan)

        db.commit()

        db.refresh(scan)

        return scan.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_scan_by_id(scan_id: int):

    db = SessionLocal()

    try:
        return (
            db.query(Scan)
            .filter(Scan.id == scan_id)
            .first()
        )

    finally:
        db.close()