from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io
import csv

router = APIRouter()

@router.get("/reports/csv")
async def get_csv_report():
    # Placeholder CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Client", "Project", "Amount", "Date"])
    writer.writerow(["Client A", "Project X", "1000", "2024-06-01"])
    writer.writerow(["Client B", "Project Y", "1500", "2024-06-02"])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=report.csv"})

@router.get("/reports/pdf")
async def get_pdf_report():
    # Placeholder PDF generation
    pdf_content = b"%PDF-1.4\n%âãÏÓ\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Report PDF Placeholder) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000111 00000 n \n0000000212 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n312\n%%EOF"
    return StreamingResponse(io.BytesIO(pdf_content), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=report.pdf"})
