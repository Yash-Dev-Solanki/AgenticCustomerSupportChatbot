using System;

namespace AgenticAPI.Application.GetChatsByCustomerId
{
    public class GetChatsByCustomerIdResponseModel
    {
        public string ChatId { get; set; }
        public string CustomerId { get; set; }
        public DateTime CreatedAt { get; set; }
    }
}
