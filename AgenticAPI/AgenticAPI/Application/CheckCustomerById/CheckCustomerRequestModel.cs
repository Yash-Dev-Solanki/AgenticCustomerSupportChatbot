using MediatR;

namespace AgenticAPI.Application.CheckCustomerById
{
    public class CheckCustomerRequestModel: IRequest<CheckCustomerResponseModel>
    {
        public string? CustomerId { get; set; }
    }
}
