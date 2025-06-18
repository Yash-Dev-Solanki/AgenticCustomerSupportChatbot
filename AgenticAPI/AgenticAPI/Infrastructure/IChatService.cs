using MongoDB.Driver;
using MongoDB.Bson;
using AgenticAPI.Domain;

namespace AgenticAPI.Infrastructure
{
    public interface IChatService
    {
        public Task<bool> CreateChat(Chat newChat);
        public Task<List<Chat>> GetChatsByCustomerId(string customerId);
        public Task<Chat> GetChatById(string customerId, string chatId);
        public Task AddMessagesToChat(string chatId, List<ChatMessage> message);
        public Task<bool> ChatExists(string chatId);
    }
}
