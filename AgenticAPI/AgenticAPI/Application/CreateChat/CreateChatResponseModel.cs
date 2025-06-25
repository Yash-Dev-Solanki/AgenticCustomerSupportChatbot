using AgenticAPI.Domain;

namespace AgenticAPI.Application.CreateChat
{
    public class CreateChatResponseModel: BaseResponseModel
    {
        public string? ChatId { get; set; }
        public DateTime CreatedAt { get; set; }

        public CreateChatResponseModel(): base()
        {
        }
    }
}
