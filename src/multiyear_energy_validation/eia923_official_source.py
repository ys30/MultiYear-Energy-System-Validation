"""Download official EIA-923 annual workbook and inspect sheet schema.

Do not claim successful generator-level matching until headers and source
granularity have been reviewed. Source is EIA.gov; failures are explicit.
"""
import json
import urllib.request
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

URL = "https://www.eia.gov/electricity/data/eia923/xls/f923_2025.zip"


def inspect_archive(archive_path, output_path):
    from io import BytesIO
    results = []
    with ZipFile(archive_path) as archive:
        for name in archive.namelist():
            if not name.lower().endswith(".xlsx"):
                continue
            with archive.open(name) as source:
                book = load_workbook(BytesIO(source.read()), read_only=True, data_only=True)
            try:
                for sheet in book:
                    title = sheet.title.lower()
                    if not any(term in title for term in ("generation", "fuel", "page 1", "page 4")):
                        continue
                    rows = sheet.iter_rows(min_row=1, max_row=8, values_only=True)
                    preview = [[str(value)[:110] if value is not None else None
                                for value in row[:35]] for row in rows]
                    results.append({"workbook":name,"sheet":sheet.title,
                                    "header_preview_first_8_rows":preview})
            finally:
                book.close()
    result = {
        "source_url":URL, "source_type":"official_EIA923_annual_workbook",
        "sheets":results, "plant_generation_values_extracted":False,
        "generation_and_storage_attribution_verified":False,
        "empirical_dispatch_approved":False,
    }
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n",encoding="utf-8")
    print("EIA923_OFFICIAL_SCHEMA_AUDIT="+json.dumps({
        "source_url":URL,"sheets":[{"workbook":r["workbook"],"sheet":r["sheet"],
                                  "header_preview_first_8_rows":r["header_preview_first_8_rows"]}
                                 for r in results],
        "generation_values_extracted":False,"dispatch_approved":False,
    },sort_keys=True))
    return result


def main():
    dest = Path("outputs/eia923/2025/f923_2025.zip")
    dest.parent.mkdir(parents=True,exist_ok=True)
    request = urllib.request.Request(URL, headers={"User-Agent":"Research validation (public EIA data)"})
    with urllib.request.urlopen(request, timeout=90) as response, dest.open("wb") as stream:
        import shutil
        shutil.copyfileobj(response,stream)
    inspect_archive(dest, "outputs/spatial_weather_merged_2025/eia923_official_schema_audit.json")


if __name__ == "__main__":
    main()
