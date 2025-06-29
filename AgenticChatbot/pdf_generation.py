from fpdf import FPDF
from datetime import datetime
from dateutil.parser import isoparse
from services.loan_service import fetch_loan_statement

def generate_loan_statement_pdf(customer_id: str) -> bytes:
    data = fetch_loan_statement(customer_id)

    for p in data.paymentHistory:
        if not isinstance(p.paymentDate, datetime):
            p.paymentDate = isoparse(p.paymentDate)

    summary = data.loanSummary
    payments_raw = sorted(data.paymentHistory or [], key=lambda x: x.paymentDate)

    initial_principal = summary.loanAmount
    interest_rate_annual = summary.interestRate
    emi = summary.emiAmount
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", 'B', 16)
            self.cell(0, 10, "Loan Statement", ln=True, align="C")
            self.ln(5)

    pdf = PDF()
    pdf.add_page()
    headers = ["No.", "Date", "EMI", "Interest", "Principal", "Prev", "Curr", "Mode", "Txn ID"]
    col_widths = [10, 20, 20, 20, 22, 25, 25, 20, 40]
    alignments = ["C", "C", "R", "R", "R", "R", "R", "C", "C"]
    page_width = pdf.w - 2 * pdf.l_margin
    table_width = sum(col_widths)
    x_start = (page_width - table_width) / 2 + pdf.l_margin

    pdf.set_fill_color(230, 230, 230)  
    pdf.set_font("Arial", "B", 10)
    pdf.set_x(x_start)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Arial", size=9)
    for idx, p in enumerate(payments_raw, 1):
        values = [
            str(idx),
            p.paymentDate.strftime('%d-%b-%Y'),
            f"${p.paymentAmount:,.2f}",
            f"${p.interestPaid:,.2f}",
            f"${p.principalPaid:,.2f}",
            f"${p.previousPrincipal:,.2f}",
            f"${p.currentPrincipal:,.2f}",
            p.paymentMode,
            p.transactionId
        ]
        pdf.set_x(x_start)
        for i, val in enumerate(values):
            pdf.cell(col_widths[i], 8, val, border=1,align=alignments[i])
        pdf.ln()

    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return pdf_bytes
