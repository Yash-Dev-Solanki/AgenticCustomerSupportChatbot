using AgenticAPI.Domain;
namespace AgenticAPI.Application.StoreChatMessage
{
    public class StoreChatMessagesRequestModel
    {
        public string ChatId { get; set; }
        public string CustomerId { get; set; }
        public List<ChatMessage> Messages { get; set; }
    }
}
