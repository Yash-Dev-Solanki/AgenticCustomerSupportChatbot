using AgenticAPI.Domain;
using MediatR;

namespace AgenticAPI.Application.AddLoanPayment
{
    public class AddLoanPaymentRawRequestModel : IRequest<AddLoanPaymentResponseModel>
    {
        public LoanPayment LoanPayment { get; set; }
    }
}
