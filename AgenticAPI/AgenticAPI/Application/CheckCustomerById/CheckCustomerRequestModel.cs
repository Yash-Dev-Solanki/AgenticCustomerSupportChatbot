using MediatR;

namespace AgenticAPI.Application.CheckCustomerById
{
    public class CheckCustomerRequestModel: IRequest<CheckCustomerResponseModel>
    {
        public string? CustomerId { get; set; }
        public string? SSN { get; set; }
    }
}
