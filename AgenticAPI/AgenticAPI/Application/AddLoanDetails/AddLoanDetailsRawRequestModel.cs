using AgenticAPI.Domain;
using MediatR;

namespace AgenticAPI.Application.AddLoanDetails
{
    public class AddLoanDetailsRawRequestModel : IRequest<AddLoanDetailsResponseModel>
    {
        public LoanDetails LoanDetails { get; set; }
    }
}
