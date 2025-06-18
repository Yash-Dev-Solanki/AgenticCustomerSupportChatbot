using AgenticAPI.Infrastructure;
using MediatR;
using System.Threading;
using System.Threading.Tasks;
using AgenticAPI.Domain;

namespace AgenticAPI.Application.AddLoanDetails
{
    public class AddLoanDetailsHandler : IRequestHandler<AddLoanDetailsRawRequestModel, AddLoanDetailsResponseModel>
    {
        private readonly ILoanService _loanService;

        public AddLoanDetailsHandler(ILoanService loanService)
        {
            _loanService = loanService;
        }

        public async Task<AddLoanDetailsResponseModel> Handle(AddLoanDetailsRawRequestModel request, CancellationToken cancellationToken)
        {
            var result = await _loanService.AddLoanDetails(request.LoanDetails);
            return new AddLoanDetailsResponseModel
            {
                Success = result,
                Message = result ? "Loan details added successfully." : "Failed to add loan details."
            };
        }
    }
}
