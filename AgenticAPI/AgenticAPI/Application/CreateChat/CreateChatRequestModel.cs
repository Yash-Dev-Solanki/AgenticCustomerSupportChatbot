using MediatR;

namespace AgenticAPI.Application.CreateChat
{
    public class CreateChatRequestModel: IRequest<CreateChatResponseModel>
    {
        public string? CustomerId { get; set; }
    }
}
