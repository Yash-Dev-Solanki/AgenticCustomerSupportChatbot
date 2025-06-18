using MediatR;
using AgenticAPI.Application.GetLoanStatement;
using AgenticAPI.Domain;

namespace AgenticAPI.Application.GetLoanStatement
{
    public class GetLoanStatementRawRequestModel : IRequest<GetLoanStatementResponseModel>
    {
        public string? CustomerId { get; }

        public GetLoanStatementRawRequestModel(string customerId)
        {
            CustomerId = customerId;
        }
    }
}
