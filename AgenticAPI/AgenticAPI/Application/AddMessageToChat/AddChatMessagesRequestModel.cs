using AgenticAPI.Domain;
using MediatR;
namespace AgenticAPI.Application.AddChatMessage
{
    public class AddChatMessagesRequestModel: IRequest<AddChatMessagesResponseModel>
    {
        public string? ChatId { get; set; }
        public List<ChatMessage>? Messages { get; set; }
    }
}
