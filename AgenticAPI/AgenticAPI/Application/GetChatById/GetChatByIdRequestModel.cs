using MediatR;

namespace AgenticAPI.Application.GetChatById
{
    public class GetChatByIdRequestModel: IRequest<GetChatByIdResponseModel>
    {
        public string? ChatId { get; set; }
    }
}
