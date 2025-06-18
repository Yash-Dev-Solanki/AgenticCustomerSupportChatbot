using System;
using System.Collections.Generic;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;


namespace AgenticAPI.Domain
{
    public class Chat
    {
        [BsonId]
        [BsonRepresentation(BsonType.ObjectId)]
        public string ChatId { get; set; }
        public string CustomerId { get; set; }
        public DateTime CreatedAt { get; set; }
        public List<ChatMessage> Messages { get; set; } = new List<ChatMessage>();
    }
    public class ChatMessage
    {
        public string Sender { get; set; } 
        public string Message { get; set; }
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }
}

