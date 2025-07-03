from fpdf import FPDF
from datetime import datetime

class LoanStatementPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Loan Statement", ln=True, align="C")
        self.ln(10)

def generate_dummy_loan_statement_pdf():
    pdf = LoanStatementPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Dummy customer/loan summary
    summary = [
        "Loan Account Number: LN-000123456",
        "Loan Amount: $500,000.00",
        "Interest Rate: 7.5%",
        "Tenure: 60 months",
        "EMI Amount: $10,123.45",
        f"Start Date: {datetime.today().strftime('%d-%b-%Y')}",
        "Status: Active"
    ]

    for line in summary:
        pdf.cell(0, 10, line, ln=True)

    pdf.ln(10)

    # Table header
    headers = ["No.", "Date", "EMI", "Interest", "Principal", "Prev", "Curr", "Mode", "Txn ID"]
    col_widths = [10, 25, 22, 25, 25, 25, 25, 20, 30]
    payments = [
        ("1", "01-Jan-2024", "$10,123.45", "$2,500.00", "$7,623.45", "$500,000", "$492,376.55", "NEFT", "TXN001"),
        ("2", "01-Feb-2024", "$10,123.45", "$2,461.88", "$7,661.57", "$492,376.55", "$484,714.98", "UPI", "TXN002"),
        ("3", "01-Mar-2024", "$10,123.45", "$2,423.57", "$7,699.88", "$484,714.98", "$477,015.10", "Cash", "TXN003"),
    ]
    page_width = pdf.w - 2 * pdf.l_margin
    table_width = sum(col_widths)
    x_start = (page_width - table_width) / 2 + pdf.l_margin

    pdf.set_fill_color(230, 230, 230)  # Light grey background
    pdf.set_font("Arial", "B", 10)
    pdf.set_x(x_start)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, fill=True, align="C")
    pdf.ln()

    # Dummy payment rows (centered)
    pdf.set_font("Arial", "", 10)
    for row in payments:
        pdf.set_x(x_start)
        for i, item in enumerate(row):
            pdf.cell(col_widths[i], 8, item, border=1, align="C")
        pdf.ln()

    # Dummy payment rows
    pdf.set_font("Arial", "", 10)
    

    pdf.output("dummy_loan_statement.pdf")
    print("PDF created: dummy_loan_statement.pdf")

if __name__ == "__main__":
    generate_dummy_loan_statement_pdf()
