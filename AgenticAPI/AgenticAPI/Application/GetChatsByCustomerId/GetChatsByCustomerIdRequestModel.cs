using MediatR;

namespace AgenticAPI.Application.GetChatsByCustomerId
{
    public class GetChatsByCustomerIdRequestModel: IRequest<GetChatsByCustomerIdResponseModel>
    {
        public string? CustomerId { get; set; }
    }
}
