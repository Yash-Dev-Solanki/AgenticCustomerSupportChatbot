using System.ComponentModel.DataAnnotations;
using AgenticAPI.Domain;
using System;
using System.Net;

namespace AgenticAPI.Application.GetLoanStatement
{
    public class GetLoanStatementResponseModel: BaseResponseModel
    {
        public bool Success { get; set; } = true;
        public HttpStatusCode StatusCode { get; set; } = HttpStatusCode.OK;
        public List<string>? Errors { get; set; } = new();

        public string? CustomerId { get; set; }
        public string? LoanAccountNumber { get; set; }
        public LoanSummary? LoanSummary { get; set; }
        public List<LoanPayment>? PaymentHistory { get; set; }
    }
    public class LoanSummary
    {
        public double LoanAmount { get; set; }
        public double InterestRate { get; set; }
        public int TenureMonths { get; set; }
        public double EmiAmount { get; set; }
        public DateTime StartDate { get; set; }
        public string? Status { get; set; }
    }

    public class LoanPayment
    {
        public DateTime PaymentDate { get; set; }
        public double AmountPaid { get; set; }
        public string? PaymentMode { get; set; }
        public string? Status { get; set; }
        public string? LoanAccountNumber { get; set; }  
        public string? TransactionId { get; set; }      
    }
}
