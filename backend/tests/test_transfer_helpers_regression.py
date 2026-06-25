from __future__ import annotations

import os
import re
from datetime import date

import pytest

# Prevent import-time failures in backend.database when running tests outside Docker
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./_placeholder_test.db")

from backend.routers.transfer import ResponseFormat, _build_filename, resolve_format


# --- _build_filename ------------------------------------------------------------

def test_build_filename_defaults_to_dated_name_when_none() -> None:
    result = _build_filename(None, "csv")
    assert result == f"transfer-{date.today():%Y%m%d}.csv"


def test_build_filename_appends_missing_extension() -> None:
    assert _build_filename("grades", "csv") == "grades.csv"


def test_build_filename_keeps_matching_extension() -> None:
    assert _build_filename("grades.csv", "csv") == "grades.csv"


def test_build_filename_corrects_wrong_extension() -> None:
    # A name carrying a different extension is forced to the requested format.
    assert _build_filename("grades.txt", "csv") == "grades.csv"
    assert _build_filename("report.final", "xlsx") == "report.xlsx"


@pytest.mark.parametrize("blank", ["", "   ", "\t"])
def test_build_filename_falls_back_to_default_for_blank_names(blank: str) -> None:
    assert _build_filename(blank, "csv") == f"transfer-{date.today():%Y%m%d}.csv"


def test_build_filename_strips_path_traversal_components() -> None:
    # os.path.basename must defuse any directory traversal in the caller value so
    # the Content-Disposition filename can never point outside a bare filename.
    assert _build_filename("../../etc/passwd", "csv") == "passwd.csv"
    assert _build_filename("/var/tmp/report.xlsx", "xlsx") == "report.xlsx"


# --- resolve_format -------------------------------------------------------------

def test_resolve_format_query_override_wins_over_accept_header() -> None:
    # A non-empty override short-circuits Accept-header negotiation.
    assert resolve_format("text/csv", ResponseFormat.XLSX) == ResponseFormat.XLSX


@pytest.mark.parametrize(
    ("accept", "expected"),
    [
        ("application/json", ResponseFormat.JSON),
        ("text/csv", ResponseFormat.CSV),
        (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ResponseFormat.XLSX,
        ),
        ("application/vnd.oasis.opendocument.spreadsheet", ResponseFormat.ODS),
    ],
)
def test_resolve_format_matches_accept_header(accept: str, expected: ResponseFormat) -> None:
    assert resolve_format(accept, None) == expected


@pytest.mark.parametrize("accept", ["", "*/*", "text/html", "application/xml"])
def test_resolve_format_defaults_to_json_when_unmatched(accept: str) -> None:
    assert resolve_format(accept, None) == ResponseFormat.JSON
