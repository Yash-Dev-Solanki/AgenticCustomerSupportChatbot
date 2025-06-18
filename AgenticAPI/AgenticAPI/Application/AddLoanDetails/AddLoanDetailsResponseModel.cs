using MediatR;
using AgenticAPI.Domain;

namespace AgenticAPI.Application.AddLoanDetails
{
    public class AddLoanDetailsResponseModel
    {
        public bool Success { get; set; }
        public string Message { get; set; }
    }
}
