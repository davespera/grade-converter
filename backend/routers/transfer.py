from __future__ import annotations
import io
import csv
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response, JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from .. import database, models, crud
from ..auth import handle_api_key
from datetime import date
import pandas as pd
import os

router = APIRouter(
    prefix="/transfer",
    tags=["Transfer Logic"],
)


class ResponseFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"
    ODS = "ods"


_MEDIA_TYPES = {
    ResponseFormat.JSON: "application/json",
    ResponseFormat.CSV: "text/csv",
    ResponseFormat.XLSX: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ResponseFormat.ODS: "application/vnd.oasis.opendocument.spreadsheet",
}

_MEDIA_EXTENSIONS = {
    ResponseFormat.JSON: "json",
    ResponseFormat.CSV: "csv",
    ResponseFormat.XLSX: "xlsx",
    ResponseFormat.ODS: "ods",
}

def resolve_format(accept: str, fmt_override: str | None) -> ResponseFormat:
    """Query param overrides header (for debugging or HTML forms)"""
    if fmt_override:
        return fmt_override
    for fmt, mime in _MEDIA_TYPES.items():
        if mime in accept:
            return fmt
    return ResponseFormat.JSON # default


#def _conversion_headers() -> list[str]:
#    return ["subject", "origin_grade", "converted_5_10", "converted_literal"]


def _build_filename(requested_name: str | None, extension: str) -> str:
    default_base = f"transfer-{date.today():%Y%m%d}"
    base = (requested_name or default_base).strip()
    base = os.path.basename(base)
    if not base:
        base = default_base

    root, ext = os.path.splitext(base)
    if not root:
        root = default_base

    desired_ext = f".{extension}"
    if ext.lower() != desired_ext:
        return f"{root}{desired_ext}"
    return f"{root}{ext}"

def build_file_response(
    conversion: list[models.GradeOutput],
    fmt: ResponseFormat,
    requested_name: str | None = None,
) -> Response:
    rows = [
        {
            "subject":           g.subject,
            "origin_grade":      g.origin_grade,
            "converted_5_10":    g.converted_5_10,
            "converted_literal": g.converted_literal,
        }
        for g in conversion
    ]
    df = pd.DataFrame(rows)

    if fmt == ResponseFormat.CSV:
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        return Response(
            content=buf.getvalue(),
            media_type=_MEDIA_TYPES[ResponseFormat.CSV],
            headers={"Content-Disposition": f"attachment; filename={_build_filename(requested_name, _MEDIA_EXTENSIONS[ResponseFormat.CSV])}"},
        )

    buf = io.BytesIO()
    if fmt == ResponseFormat.XLSX:
        df.to_excel(buf, index=False, engine="openpyxl")
        media_type = _MEDIA_TYPES[ResponseFormat.XLSX]
        fname = _build_filename(requested_name, _MEDIA_EXTENSIONS[ResponseFormat.XLSX])
    elif fmt == ResponseFormat.ODS:
        df.to_excel(buf, index=False, engine="odf")
        media_type = _MEDIA_TYPES[ResponseFormat.ODS]
        fname = _build_filename(requested_name, _MEDIA_EXTENSIONS[ResponseFormat.ODS])

    return Response(
        content=buf.getvalue(),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={fname}"},
    )


@router.post("/", response_model=models.TransferResponse, operation_id="convert_grade")
async def convert_grade(
    request: models.TransferRequest,
    http_request: Request,
    db: AsyncSession = Depends(database.get_database_session),
    format: ResponseFormat | None = Query(default=None),
    filename: str | None = Query(default=None), 
):

    conversion = []

    for grade in request.grades:
        # Find the scale
        scale = await crud.get_scale(db, scale_id=request.scale_id)
        
        if not scale:
            raise HTTPException(status_code=404, detail="Academic scale not found")
        
        # Find the specific equivalence
        equivalence = await crud.get_grade_equivalence(db, scale_id=request.scale_id, origin_grade=grade.origin_grade)
        
        if not equivalence:
            raise HTTPException(status_code=404, detail="No equivalence found for this grade")
            
        # Map DB model to GradeOutput schema
        conversion.append(
            models.GradeOutput(
                subject=grade.subject,
                origin_grade=equivalence.origin_grade,
                converted_5_10=equivalence.spanish_5_10,
                converted_literal=equivalence.spanish_literal.value,
            )
        )

    fmt = resolve_format(http_request.headers.get("accept", ""), format)

    if fmt == ResponseFormat.JSON:
        return models.TransferResponse(conversion=conversion)

    return build_file_response(conversion, fmt, filename)