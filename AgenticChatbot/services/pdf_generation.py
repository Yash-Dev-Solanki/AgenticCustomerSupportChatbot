from fpdf import FPDF
from io import BytesIO
import pandas as pd

def generate_pdf_bytes(payments: list) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=10)

    headers = ["No.", "Date", "EMI", "Interest", "Principal", "Previous Principal", "Current Principal", "Mode", "Txn ID"]
    col_widths = [10, 20, 20, 20, 22, 22, 22, 25, 30]

    for header, width in zip(headers, col_widths):
        pdf.cell(width, 8, header, 1, 0, 'C')
    pdf.ln()

    for idx, p in enumerate(payments, 1):
        row_values = [
            str(idx),
            p.get("Date", ""),
            p.get("EMI", ""),
            p.get("Interest", ""),
            p.get("Principal", ""),
            p.get("Previous Principal", ""),
            p.get("Current Principal", ""),
            p.get("Payment Mode") or p.get("Mode") or "-",
            p.get("Transaction ID", "")
        ]
        for value, width in zip(row_values, col_widths):
            pdf.cell(width, 12, str(value), 1)
        pdf.ln()
    pdf_bytes_str = pdf.output(dest='S').encode('latin1')
    return pdf_bytes_str


def generate_excel_bytes(payments: list) -> bytes:
    df = pd.DataFrame(payments)
    if 'Payment Mode' in df.columns:
        df = df.rename(columns={'Payment Mode': 'Mode'})

    columns_order = ["Date", "EMI", "Interest", "Principal", "Previous Principal",
                     "Current Principal", "Mode", "Transaction ID"]
    columns_order_filtered = [col for col in columns_order if col in df.columns]

    df = df[columns_order_filtered]

    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer.read()
