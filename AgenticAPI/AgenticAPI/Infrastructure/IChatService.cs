using MongoDB.Driver;
using MongoDB.Bson;
using AgenticAPI.Domain;

namespace AgenticAPI.Infrastructure
{
    public interface IChatService
    {
        public Task<bool> CreateChat(Chat newChat);
        public Task<List<ChatSummary>> GetChatsByCustomerId(string customerId);
        public Task<Chat?> GetByChatId(string chatId);
        public Task<bool> AddMessagesToChat(string chatId, List<ChatMessage> message);
        public Task<Chat?> UpdateChatDetails(string chatId, string fieldToUpdate, object newValue);
    }
}
