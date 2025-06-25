using System;
using AgenticAPI.Domain;

namespace AgenticAPI.Application.GetChatsByCustomerId
{
    public class GetChatsByCustomerIdResponseModel: BaseResponseModel
    {
        public List<string>? ChatIds { get; set; }

        public GetChatsByCustomerIdResponseModel(): base()
        {
        }
    }
}
