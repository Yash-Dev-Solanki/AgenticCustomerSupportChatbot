using AgenticAPI.Infrastructure;
using MediatR;
using System.Threading;
using System.Threading.Tasks;

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
            var result = await _loanService.AddLoanPayment(request.LoanPayment);
            return new AddLoanPaymentResponseModel
            {
                Success = result,
                Message = result ? "Loan payment added successfully." : "Failed to add loan payment."
            };
        }
    }
}
