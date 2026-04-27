"""
Assessments (past papers) — Cloudflare R2 backed.

Files live in the R2 bucket under:
    assessments/grade-{N}/term-{T}/{subject-slug}-{year}.{pdf|docx}

where:
  - grade slug is the grade.name lowercased with spaces → hyphens
    ("Grade 6" → "grade-6", "PP1" → "pp1").
  - subject is a free-text slug (kebab-case) to keep this admin-tool simple.
  - year is a 4-digit year.

Nothing about the paper catalogue lives in MongoDB — we list straight from R2.
The only DB write is `wallet_transactions` on each paid download, for the
existing finance audit trail.

Teacher download flow (pay-every-time by design decision):
  POST /api/assessments/download    → wallet check → atomic debit → signed URL
    402 if insufficient funds (frontend shows the top-up prompt).

Admin upload flow:
  POST /api/admin/assessments/upload  (multipart)
  DELETE /api/admin/assessments       body={"key": "..."}
"""
from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel
from bson import ObjectId

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, BotoCoreError

from app.deps import (
    api_router,
    db,
    verify_token,
    verify_admin,
    ASSESSMENT_DOWNLOAD_COST_KES,
)

# ---------------------------------------------------------------------------
# R2 client (lazy — built once per process)
# ---------------------------------------------------------------------------

_r2_client = None


def _get_r2_client():
    global _r2_client
    if _r2_client is not None:
        return _r2_client
    account_id = os.environ.get("R2_ACCOUNT_ID")
    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    if not (account_id and access_key and secret_key):
        raise HTTPException(
            status_code=503,
            detail="Assessments storage is not configured. Contact the administrator.",
        )
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    _r2_client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )
    return _r2_client


def _bucket() -> str:
    b = os.environ.get("R2_BUCKET")
    if not b:
        raise HTTPException(
            status_code=503,
            detail="Assessments bucket is not configured.",
        )
    return b


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ALLOWED_EXTS = {".pdf", ".doc", ".docx"}
_ALLOWED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}


def _grade_slug(grade_name: str) -> str:
    return re.sub(r"\s+", "-", grade_name.strip().lower())


def _slugify_subject(raw: str) -> str:
    """Admin-supplied subject → kebab-case safe slug."""
    s = re.sub(r"[^a-zA-Z0-9]+", "-", raw).strip("-").lower()
    return s or "general"


def _parse_filename_meta(filename: str) -> dict:
    """Reverse _build_key: pull subject + year out of the stored file name.

    Tolerates arbitrary files uploaded manually too — anything that doesn't
    match the pattern still lists cleanly with best-effort fields.
    """
    base = filename.rsplit("/", 1)[-1]
    name, _, ext = base.rpartition(".")
    ext = f".{ext.lower()}" if ext else ""
    m = re.match(r"^(?P<subject>.+?)-(?P<year>\d{4})$", name)
    if m:
        subj_slug = m.group("subject")
        year = int(m.group("year"))
    else:
        subj_slug = name or "assessment"
        year = None
    title = subj_slug.replace("-", " ").title()
    if year:
        title = f"{title} — {year}"
    return {
        "subjectSlug": subj_slug,
        "subjectName": subj_slug.replace("-", " ").title(),
        "year": year,
        "title": title,
        "ext": ext,
    }


def _build_key(grade_slug: str, term: int, subject_slug: str, year: int, ext: str) -> str:
    return f"assessments/{grade_slug}/term-{term}/{subject_slug}-{year}{ext}"


def _validate_grade_term(grade_slug: str, term: int) -> None:
    if not re.match(r"^(grade-\d{1,2}|pp\d)$", grade_slug):
        raise HTTPException(status_code=400, detail="Invalid grade")
    if term not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Term must be 1, 2, or 3")


# ---------------------------------------------------------------------------
# Teacher endpoints
# ---------------------------------------------------------------------------

@api_router.get("/assessments")
async def list_assessments(
    gradeId: str = Query(...),
    term: int = Query(..., ge=1, le=3),
    _user: dict = Depends(verify_token),
):
    """List all assessments in R2 for a given grade + term.

    Returns [{id, key, subjectName, year, title, sizeBytes, ext, uploadedAt}].
    """
    try:
        grade_oid = ObjectId(gradeId)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid gradeId")
    grade = await db.grades.find_one({"_id": grade_oid}, {"_id": 0, "name": 1})
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    grade_slug = _grade_slug(grade["name"])
    _validate_grade_term(grade_slug, term)
    prefix = f"assessments/{grade_slug}/term-{term}/"

    client = _get_r2_client()
    try:
        resp = client.list_objects_v2(Bucket=_bucket(), Prefix=prefix)
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(status_code=502, detail=f"Storage unavailable: {e}")

    items = []
    for obj in resp.get("Contents", []) or []:
        key = obj["Key"]
        if key.endswith("/"):
            continue  # skip folder markers
        meta = _parse_filename_meta(key)
        items.append({
            "id": key,  # R2 key IS the id
            "key": key,
            "subjectName": meta["subjectName"],
            "year": meta["year"],
            "title": meta["title"],
            "ext": meta["ext"],
            "sizeBytes": obj.get("Size", 0),
            "uploadedAt": obj.get("LastModified").isoformat() if obj.get("LastModified") else None,
        })
    # Stable ordering: subject asc, year desc
    items.sort(key=lambda x: (x["subjectName"].lower(), -(x["year"] or 0)))

    return {
        "gradeId": gradeId,
        "gradeName": grade["name"],
        "term": term,
        "costPerDownload": ASSESSMENT_DOWNLOAD_COST_KES,
        "items": items,
    }


class AssessmentDownloadRequest(BaseModel):
    key: str


@api_router.post("/assessments/download")
async def download_assessment(
    payload: AssessmentDownloadRequest,
    user: dict = Depends(verify_token),
):
    """Charge the wallet (pay-every-time) and return a short-lived signed URL."""
    key = payload.key.strip()
    if not key.startswith("assessments/") or ".." in key:
        raise HTTPException(status_code=400, detail="Invalid assessment key")

    # 1. Ensure the object exists (avoid charging for a missing file)
    client = _get_r2_client()
    try:
        client.head_object(Bucket=_bucket(), Key=key)
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        if code in ("404", "NoSuchKey", "NotFound"):
            raise HTTPException(status_code=404, detail="Assessment not found")
        raise HTTPException(status_code=502, detail=f"Storage error: {code or e}")
    except BotoCoreError as e:
        raise HTTPException(status_code=502, detail=f"Storage unavailable: {e}")

    # 2. Atomic wallet debit — same pattern the scheme download uses
    user_id = user["_id"] if isinstance(user.get("_id"), ObjectId) else ObjectId(str(user["_id"]))
    res = await db.users.find_one_and_update(
        {"_id": user_id, "walletBalance": {"$gte": ASSESSMENT_DOWNLOAD_COST_KES}},
        {"$inc": {"walletBalance": -ASSESSMENT_DOWNLOAD_COST_KES}},
        return_document=True,
    )
    if not res:
        current = await db.users.find_one({"_id": user_id}, {"walletBalance": 1, "_id": 0})
        bal = float((current or {}).get("walletBalance", 0) or 0)
        raise HTTPException(
            status_code=402,
            detail={
                "message": "Your wallet is running low. Top up to keep enjoying high-quality assessments.",
                "balance": bal,
                "required": ASSESSMENT_DOWNLOAD_COST_KES,
            },
        )

    # 3. Record the transaction for audit
    try:
        await db.wallet_transactions.insert_one({
            "userId": str(user_id),
            "type": "assessment_download",
            "amount": -ASSESSMENT_DOWNLOAD_COST_KES,
            "balanceAfter": float(res.get("walletBalance", 0) or 0),
            "key": key,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass  # audit write failure must never block the user's download

    # 4. Sign a URL valid for 10 minutes
    try:
        signed_url = client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": _bucket(),
                "Key": key,
                "ResponseContentDisposition": f'attachment; filename="{key.rsplit("/", 1)[-1]}"',
            },
            ExpiresIn=600,
        )
    except (ClientError, BotoCoreError) as e:
        # Refund — the user shouldn't pay if we can't deliver the file
        await db.users.update_one(
            {"_id": user_id},
            {"$inc": {"walletBalance": ASSESSMENT_DOWNLOAD_COST_KES}},
        )
        raise HTTPException(status_code=502, detail=f"Download signing failed: {e}")

    return {
        "signedUrl": signed_url,
        "expiresInSeconds": 600,
        "charged": ASSESSMENT_DOWNLOAD_COST_KES,
        "newBalance": float(res.get("walletBalance", 0) or 0),
    }


# ---------------------------------------------------------------------------
# Admin endpoints
# ---------------------------------------------------------------------------

@api_router.post("/admin/assessments/upload")
async def admin_upload_assessment(
    file: UploadFile = File(...),
    gradeId: str = Form(...),
    term: int = Form(...),
    subject: str = Form(...),
    year: int = Form(...),
    _admin: dict = Depends(verify_admin),
):
    """Upload a single PDF / .doc / .docx into R2 under the canonical path."""
    if term not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Term must be 1, 2, or 3")
    if not (2000 <= year <= 2100):
        raise HTTPException(status_code=400, detail="Year must be between 2000 and 2100")

    try:
        grade_oid = ObjectId(gradeId)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid gradeId")
    grade = await db.grades.find_one({"_id": grade_oid}, {"_id": 0, "name": 1})
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    grade_slug = _grade_slug(grade["name"])

    # Resolve extension from content-type first, then fall back to filename
    ext = _ALLOWED_CONTENT_TYPES.get(file.content_type or "")
    if not ext:
        name_ext = os.path.splitext(file.filename or "")[1].lower()
        if name_ext in _ALLOWED_EXTS:
            ext = name_ext
    if not ext:
        raise HTTPException(
            status_code=415,
            detail="Only PDF and Microsoft Word (.doc, .docx) files are accepted.",
        )

    subject_slug = _slugify_subject(subject)
    key = _build_key(grade_slug, term, subject_slug, year, ext)
    body = await file.read()
    if not body:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    client = _get_r2_client()
    try:
        client.put_object(
            Bucket=_bucket(),
            Key=key,
            Body=body,
            ContentType=file.content_type or "application/octet-stream",
        )
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(status_code=502, detail=f"Upload failed: {e}")

    return {
        "success": True,
        "key": key,
        "sizeBytes": len(body),
        "gradeName": grade["name"],
        "term": term,
        "subjectName": subject.strip().title(),
        "year": year,
    }


class AdminAssessmentDeleteRequest(BaseModel):
    key: str


@api_router.delete("/admin/assessments")
async def admin_delete_assessment(
    payload: AdminAssessmentDeleteRequest,
    _admin: dict = Depends(verify_admin),
):
    key = payload.key.strip()
    if not key.startswith("assessments/") or ".." in key:
        raise HTTPException(status_code=400, detail="Invalid assessment key")
    client = _get_r2_client()
    try:
        client.delete_object(Bucket=_bucket(), Key=key)
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(status_code=502, detail=f"Delete failed: {e}")
    return {"success": True, "key": key}


@api_router.get("/admin/assessments")
async def admin_list_assessments(
    gradeId: Optional[str] = Query(None),
    term: Optional[int] = Query(None, ge=1, le=3),
    _admin: dict = Depends(verify_admin),
):
    """Admin-only listing — supports listing the entire bucket or a narrow slice."""
    client = _get_r2_client()
    prefix = "assessments/"
    if gradeId:
        try:
            grade_oid = ObjectId(gradeId)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid gradeId")
        grade = await db.grades.find_one({"_id": grade_oid}, {"_id": 0, "name": 1})
        if not grade:
            raise HTTPException(status_code=404, detail="Grade not found")
        grade_slug = _grade_slug(grade["name"])
        prefix = f"assessments/{grade_slug}/"
        if term:
            prefix = f"{prefix}term-{term}/"

    try:
        resp = client.list_objects_v2(Bucket=_bucket(), Prefix=prefix)
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(status_code=502, detail=f"Storage unavailable: {e}")
    items = []
    for obj in resp.get("Contents", []) or []:
        key = obj["Key"]
        if key.endswith("/"):
            continue
        parts = key.split("/")
        grade_part = parts[1] if len(parts) > 1 else ""
        term_part = parts[2] if len(parts) > 2 else ""
        meta = _parse_filename_meta(key)
        items.append({
            "key": key,
            "grade": grade_part,
            "term": term_part,
            "subjectName": meta["subjectName"],
            "year": meta["year"],
            "sizeBytes": obj.get("Size", 0),
            "uploadedAt": obj.get("LastModified").isoformat() if obj.get("LastModified") else None,
        })
    items.sort(key=lambda x: (x["grade"], x["term"], x["subjectName"].lower(), -(x["year"] or 0)))
    return {"items": items, "count": len(items)}
