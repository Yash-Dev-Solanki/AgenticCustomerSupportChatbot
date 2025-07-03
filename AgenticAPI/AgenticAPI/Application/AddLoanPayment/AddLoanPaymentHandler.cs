using AgenticAPI.Infrastructure;
using MediatR;
using System.Threading;
using System.Threading.Tasks;
using AgenticAPI.Domain;
namespace AgenticAPI.Application.AddLoanPayment
{
    public class AddLoanPaymentHandler : IRequestHandler<AddLoanPaymentRawRequestModel, AddLoanPaymentResponseModel>
    {
        private readonly ILoanService _loanService;

        public AddLoanPaymentHandler(ILoanService loanService)
        {
            _loanService = loanService;
        }

        public async Task<AddLoanPaymentResponseModel> Handle(AddLoanPaymentRawRequestModel request, CancellationToken cancellationToken)
        {
            var loanPayment = new LoanPayment
            {
                CustomerId = request.CustomerId,
                LoanAccountNumber = request.LoanAccountNumber,
                PaymentDate = request.PaymentDate,
                PaymentAmount = request.PaymentAmount,
                PaymentMode = request.PaymentMode,
                TransactionId = request.TransactionId
            };

            var result = await _loanService.AddLoanPayment(loanPayment);
            return new AddLoanPaymentResponseModel
            {
                Success = result,
                Message = result ? "Loan payment added successfully." : "Failed to add loan payment."
            };
        }

    }
}
