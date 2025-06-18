using MediatR;
using AgenticAPI.Domain;
namespace AgenticAPI.Application.AddLoanPayment
{
    public class AddLoanPaymentResponseModel
    {
        public bool Success { get; set; }
        public string Message { get; set; }
    }
}
