using AgenticAPI.Domain;
using MediatR;

namespace AgenticAPI.Application.AddLoanPayment
{
    public class AddLoanPaymentRawRequestModel : IRequest<AddLoanPaymentResponseModel>
    {
        public string CustomerId { get; set; }
        public string LoanAccountNumber { get; set; }
        public DateTime PaymentDate { get; set; }
        public double PaymentAmount { get; set; }
        public string PaymentMode { get; set; }
        public string TransactionId { get; set; }
    }
}
