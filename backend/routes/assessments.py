"""
Assessments (past papers) — Cloudflare R2 backed.

Files live in the R2 bucket under:
    assessments/grade-{N}/term-{T}/{subject-slug}-{year}.{pdf|docx}

where:
  - grade slug is the grade.name lowercased with spaces → hyphens
    ("Grade 6" → "grade-6", "PP1" → "pp1").
  - subject is a free-text slug (kebab-case) to keep this admin-tool simple.
  - year is a 4-digit year.

Nothing about the paper catalogue itself lives in MongoDB — we list straight
from R2. The only DB writes are `wallet_transactions` on each paid download
(existing finance audit trail) and `assessment_strands` (admin-maintained
curriculum-strand tags per paper, keyed by R2 key).

Teacher download flow (pay-every-time by design decision):
  POST /api/assessments/download    → wallet check → atomic debit → signed URL
    402 if insufficient funds (frontend shows the top-up prompt).

Admin upload flow:
  POST /api/admin/papers/upload       (multipart)
  DELETE /api/admin/papers            body={"key": "..."}
  GET /api/admin/papers               list, optionally filtered by grade/term
  PUT /api/admin/papers/strands       body={"key","subjectId","strandIds"}

NOTE: these live under /admin/papers, not /admin/assessments — the latter
path is already taken by an unrelated, pre-existing SLO evaluation-criteria
endpoint elsewhere in server.py (a different `db.assessments` collection).
Registering these routes under the same path silently shadowed them.
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
    # Match both plain keys (biology-2024) and suffixed keys (biology-2024-2)
    m = re.match(r"^(?P<subject>.+?)-(?P<year>\d{4})(?:-(?P<suffix>\d+))?$", name)
    if m:
        subj_slug = m.group("subject")
        year = int(m.group("year"))
        suffix = m.group("suffix")  # e.g. "2", "3" or None for the first paper
    else:
        subj_slug = name or "assessment"
        year = None
        suffix = None
    title = subj_slug.replace("-", " ").title()
    if year:
        title = f"{title} — {year}"
    if suffix:
        title = f"{title} ({suffix})"
    return {
        "subjectSlug": subj_slug,
        "subjectName": subj_slug.replace("-", " ").title(),
        "year": year,
        "suffix": int(suffix) if suffix else 1,
        "title": title,
        "ext": ext,
    }


def _build_key(grade_slug: str, term: int, subject_slug: str, year: int, ext: str) -> str:
    return f"assessments/{grade_slug}/term-{term}/{subject_slug}-{year}{ext}"


def _next_available_key(
    client,
    bucket: str,
    grade_slug: str,
    term: int,
    subject_slug: str,
    year: int,
    ext: str,
) -> str:
    """Return the next non-colliding R2 key for this subject/year/grade/term.

    Strategy:
      - First candidate: assessments/{grade}/term-{N}/{subject}-{year}.{ext}
      - If that key already exists in R2, try:
          assessments/{grade}/term-{N}/{subject}-{year}-2.{ext}
          assessments/{grade}/term-{N}/{subject}-{year}-3.{ext}
          ... up to suffix 99.

    A single R2 list_objects_v2 call with a tight prefix is enough to find
    all existing papers for this subject/year — no extra API calls needed.
    """
    base_prefix = f"assessments/{grade_slug}/term-{term}/{subject_slug}-{year}"
    try:
        resp = client.list_objects_v2(Bucket=bucket, Prefix=base_prefix)
    except (ClientError, BotoCoreError):
        # Listing failed — fall back to plain key (old behaviour, still safe)
        return _build_key(grade_slug, term, subject_slug, year, ext)

    existing_keys = {obj["Key"] for obj in resp.get("Contents", []) or []}

    # First candidate: no suffix
    candidate = _build_key(grade_slug, term, subject_slug, year, ext)
    if candidate not in existing_keys:
        return candidate

    # Try numeric suffixes: -2, -3, ... -99
    for n in range(2, 100):
        candidate = f"assessments/{grade_slug}/term-{term}/{subject_slug}-{year}-{n}{ext}"
        if candidate not in existing_keys:
            return candidate

    # Extremely unlikely fallback: timestamp suffix guarantees uniqueness
    ts = int(datetime.now(timezone.utc).timestamp())
    return f"assessments/{grade_slug}/term-{term}/{subject_slug}-{year}-{ts}{ext}"



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

    # Attach strand tags (admin-maintained, keyed by R2 key) so teachers can
    # see which curriculum areas each paper covers before downloading.
    if items:
        tag_docs = await db.assessment_strands.find(
            {"key": {"$in": [i["key"] for i in items]}},
            {"_id": 0, "key": 1, "strandNames": 1},
        ).to_list(len(items))
        strands_by_key = {d["key"]: d.get("strandNames", []) for d in tag_docs}
        for i in items:
            i["strands"] = strands_by_key.get(i["key"], [])

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
    # verify_token returns serialize_doc(user) which renames _id → id (string).
    # We must reconstruct the ObjectId from that string field.
    raw_id = user.get("_id") or user.get("id")
    if not raw_id:
        raise HTTPException(status_code=401, detail="User identity could not be resolved.")
    user_id = raw_id if isinstance(raw_id, ObjectId) else ObjectId(str(raw_id))
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

@api_router.post("/admin/papers/upload")
async def admin_upload_assessment(
    files: List[UploadFile] = File(...),
    gradeId: str = Form(...),
    term: int = Form(...),
    subject: str = Form(...),
    year: int = Form(...),
    _admin: dict = Depends(verify_admin),
):
    """Upload 1–5 PDF / .doc / .docx files into R2 under the canonical path.

    All files share the same grade, term, subject, and year.
    Each file gets a non-colliding key via _next_available_key():
      biology-2024.pdf, biology-2024-2.pdf, biology-2024-3.pdf …

    Files are uploaded sequentially (not in parallel) so that key allocation
    is race-condition-free — each upload resolves its key only after the
    previous one has been written to R2.

    Returns a summary list — one entry per file — with individual success/error
    status so a partial failure does not roll back already-uploaded papers.
    """
    _MAX_FILES = 5

    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")
    if len(files) > _MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {_MAX_FILES} files per upload session. You submitted {len(files)}.",
        )
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
    subject_slug = _slugify_subject(subject)
    client = _get_r2_client()
    bucket = _bucket()

    results = []

    for idx, file in enumerate(files, start=1):
        # Resolve file extension
        ext = _ALLOWED_CONTENT_TYPES.get(file.content_type or "")
        if not ext:
            name_ext = os.path.splitext(file.filename or "")[1].lower()
            if name_ext in _ALLOWED_EXTS:
                ext = name_ext
        if not ext:
            results.append({
                "index": idx,
                "filename": file.filename,
                "success": False,
                "error": "Unsupported file type. Only PDF and Word (.doc, .docx) are accepted.",
            })
            continue

        body = await file.read()
        if not body:
            results.append({
                "index": idx,
                "filename": file.filename,
                "success": False,
                "error": "File is empty.",
            })
            continue

        # Resolve a non-colliding key AFTER previous file is written,
        # so sequential uploads never race for the same suffix.
        key = _next_available_key(client, bucket, grade_slug, term, subject_slug, year, ext)

        try:
            client.put_object(
                Bucket=bucket,
                Key=key,
                Body=body,
                ContentType=file.content_type or "application/octet-stream",
            )
            results.append({
                "index": idx,
                "filename": file.filename,
                "success": True,
                "key": key,
                "sizeBytes": len(body),
            })
        except (ClientError, BotoCoreError) as e:
            results.append({
                "index": idx,
                "filename": file.filename,
                "success": False,
                "error": f"Upload failed: {e}",
            })

    uploaded = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]

    return {
        "gradeName": grade["name"],
        "term": term,
        "subjectName": subject.strip().title(),
        "year": year,
        "totalSubmitted": len(files),
        "totalUploaded": len(uploaded),
        "totalFailed": len(failed),
        "results": results,
    }


class AdminAssessmentDeleteRequest(BaseModel):
    key: str


@api_router.delete("/admin/papers")
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


@api_router.get("/admin/papers")
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

    # Attach strand tags so admins can see, at a glance, which papers still
    # need tagging.
    if items:
        tag_docs = await db.assessment_strands.find(
            {"key": {"$in": [i["key"] for i in items]}},
            {"_id": 0, "key": 1, "subjectId": 1, "strandIds": 1, "strandNames": 1},
        ).to_list(len(items))
        tags_by_key = {d["key"]: d for d in tag_docs}
        for i in items:
            tag = tags_by_key.get(i["key"])
            i["subjectId"] = tag.get("subjectId") if tag else None
            i["strandIds"] = tag.get("strandIds", []) if tag else []
            i["strandNames"] = tag.get("strandNames", []) if tag else []

    items.sort(key=lambda x: (x["grade"], x["term"], x["subjectName"].lower(), -(x["year"] or 0)))
    return {"items": items, "count": len(items)}


class AssessmentStrandTagRequest(BaseModel):
    key: str
    subjectId: str
    strandIds: List[str] = []


@api_router.put("/admin/papers/strands")
async def admin_tag_assessment_strands(
    payload: AssessmentStrandTagRequest,
    _admin: dict = Depends(verify_admin),
):
    """Tag (or re-tag) which curriculum strands a given paper covers.

    `subjectId` links the paper to a real curriculum subject (the paper's own
    `subjectName` is just a free-text slug from the upload form, so this is
    kept separate rather than trying to match it by name). `strandIds` must
    belong to that subject — we look them up fresh each time so the
    denormalized `strandNames` shown to teachers can never drift out of sync
    with the curriculum.
    """
    key = payload.key.strip()
    if not key.startswith("assessments/") or ".." in key:
        raise HTTPException(status_code=400, detail="Invalid assessment key")

    try:
        subject_oid = ObjectId(payload.subjectId)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid subjectId")
    subject = await db.subjects.find_one({"_id": subject_oid}, {"_id": 0, "name": 1})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    strand_oids = []
    for sid in payload.strandIds:
        try:
            strand_oids.append(ObjectId(sid))
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid strandId: {sid}")

    strand_docs = []
    if strand_oids:
        strand_docs = await db.strands.find(
            {"_id": {"$in": strand_oids}, "subjectId": payload.subjectId},
            {"name": 1},
        ).to_list(len(strand_oids))
        if len(strand_docs) != len(strand_oids):
            raise HTTPException(
                status_code=400,
                detail="One or more strands do not belong to the selected subject.",
            )

    strand_names = [s["name"] for s in strand_docs]

    await db.assessment_strands.update_one(
        {"key": key},
        {
            "$set": {
                "key": key,
                "subjectId": payload.subjectId,
                "strandIds": payload.strandIds,
                "strandNames": strand_names,
                "updatedAt": datetime.now(timezone.utc),
            },
        },
        upsert=True,
    )

    return {
        "key": key,
        "subjectId": payload.subjectId,
        "strandIds": payload.strandIds,
        "strandNames": strand_names,
    }
