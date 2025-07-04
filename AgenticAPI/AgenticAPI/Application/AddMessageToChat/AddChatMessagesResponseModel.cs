using AgenticAPI.Domain;

namespace AgenticAPI.Application.AddChatMessage
{
    public class AddChatMessagesResponseModel: BaseResponseModel
    {
        public string? Message { get; set; }
        public AddChatMessagesResponseModel(): base()
        {
        }
    }
}
