using AgenticAPI.Domain;

namespace AgenticAPI.Application.GetChatById
{
    public class GetChatByIdResponseModel: BaseResponseModel
    {
        public Chat? chat { get; set; }

        public GetChatByIdResponseModel(): base()
        {
        }
    }
}
