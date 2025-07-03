using System;
using AgenticAPI.Domain;

namespace AgenticAPI.Application.GetChatsByCustomerId
{
    public class GetChatsByCustomerIdResponseModel: BaseResponseModel
    {
        public List<ChatSummary>? Chats { get; set; }

        public GetChatsByCustomerIdResponseModel(): base()
        {
        }
    }
}
