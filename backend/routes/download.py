from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from models.file_model import AggregatedUpload
from config.db import get_db, get_db_context
import json
from io import BytesIO
from fpdf import FPDF

router = APIRouter()

@router.get("/download/{upload_id}")
def download_aggregated(
    upload_id: int,
    format: str = Query("json", enum=["json", "pdf"])
):
    with get_db_context() as db:
        agg = db.query(AggregatedUpload).filter(AggregatedUpload.upload_id == upload_id).first()
        if not agg:
            raise HTTPException(status_code=404, detail="Aggregated data not found")

        content_json = agg.content

        if format == "json":
            file_bytes = BytesIO()
            file_bytes.write(json.dumps(content_json, indent=4).encode("utf-8"))
            file_bytes.seek(0)
            return StreamingResponse(
                file_bytes,
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=upload_{upload_id}.json"}
            )

        elif format == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)

            def add_dict_to_pdf(d, indent=0):
                for k, v in d.items():
                    if isinstance(v, dict):
                        pdf.cell(0, 6, " " * indent + str(k) + ":", ln=True)
                        add_dict_to_pdf(v, indent + 4)
                    elif isinstance(v, list):
                        pdf.cell(0, 6, " " * indent + str(k) + ":", ln=True)
                        for item in v:
                            if isinstance(item, dict):
                                add_dict_to_pdf(item, indent + 4)
                            else:
                                pdf.cell(0, 6, " " * (indent + 4) + str(item), ln=True)
                    else:
                        pdf.cell(0, 6, " " * indent + f"{k}: {v}", ln=True)

            add_dict_to_pdf(content_json)

            file_bytes = BytesIO()
            pdf.output(file_bytes)
            file_bytes.seek(0)
            return StreamingResponse(
                file_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=upload_{upload_id}.pdf"}
            )
