using System;

namespace AgenticAPI.Application.GetChatById
{
    public class GetChatByIdResponseModel
    {
        public string ChatId { get; set; }
        public string CustomerId { get; set; }
        public DateTime CreatedAt { get; set; }
        public List<ChatMessageModel> Messages { get; set; }

        public class ChatMessageModel
        {
            public string Sender { get; set; }
            public string Message { get; set; }
            public DateTime Timestamp { get; set; }
        }
    }
}
