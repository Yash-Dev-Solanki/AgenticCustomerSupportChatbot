using System;
using System.Collections.Generic;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;


namespace AgenticAPI.Domain
{
    [BsonIgnoreExtraElements]
    public class Chat
    {
        public string? ChatId { get; set; }
        public string? CustomerId { get; set; }
        public DateTime CreatedAt { get; set; }
        public List<ChatMessage> Messages { get; set; } = new List<ChatMessage>();
    }
}

