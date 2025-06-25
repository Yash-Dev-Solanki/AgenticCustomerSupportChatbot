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
    interest_rate_monthly = interest_rate_annual / 12 / 100
    emi = summary.emiAmount
    previous_principal = initial_principal

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", 'B', 16)
            self.cell(0, 10, "Loan Statement", ln=True, align="C")
            self.ln(5)

    pdf = PDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Loan Account Number: {data.loanAccountNumber}", ln=True)
    pdf.cell(0, 10, f"Loan Amount: ${initial_principal:,.2f}", ln=True)
    pdf.cell(0, 10, f"Interest Rate: {interest_rate_annual}%", ln=True)
    pdf.cell(0, 10, f"Tenure: {summary.tenureMonths} months", ln=True)
    pdf.cell(0, 10, f"EMI Amount: ${emi:,.2f}", ln=True)
    pdf.cell(0, 10, f"Start Date: {summary.startDate.strftime('%d-%b-%Y')}", ln=True)
    pdf.cell(0, 10, f"Status: {summary.status}", ln=True)
    pdf.ln(5)

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
        interest = round(previous_principal * interest_rate_monthly, 2)
        principal_paid = round(emi - interest, 2)
        current_principal = round(previous_principal - principal_paid, 2)

        values = [
            str(idx),
            p.paymentDate.strftime('%d-%b-%Y'),
            f"${emi:,.2f}",
            f"${interest:,.2f}",
            f"${principal_paid:,.2f}",
            f"${previous_principal:,.2f}",
            f"${current_principal:,.2f}",
            p.paymentMode,
            p.transactionId
        ]
        pdf.set_x(x_start)
        for i, val in enumerate(values):
            pdf.cell(col_widths[i], 8, val, border=1,align=alignments[i])
        pdf.ln()

        previous_principal = current_principal

    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return pdf_bytes
