using System;
using MongoDB.Bson;
using MongoDB.Driver;
using AgenticAPI.Domain;


namespace AgenticAPI.Infrastructure
{
    public class ChatService : IChatService
    {
        private readonly IMongoCollection<BsonDocument> _chatCollection;

        public ChatService(IConfiguration configuration)
        {
            try
            {
                var connectionString = configuration["MongoSettings:ConnectionString"];
                var database = configuration["MongoSettings:Database"];

                var client = new MongoClient(connectionString);
                var db = client.GetDatabase(database);
                _chatCollection = db.GetCollection<BsonDocument>("Chats");
            }
            catch (Exception ex)
            {
                throw new Exception("Error initializing ChatService: " + ex.Message);
            }
        }

        public async Task<bool> CreateChat(Chat newChat)
        {
            try
            {
                newChat.CreatedAt = DateTime.UtcNow;
                var doc = newChat.ToBsonDocument();
                await _chatCollection.InsertOneAsync(doc);
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine("CreateChat failed: " + ex.Message);
                return false;
            }
        }
        public async Task<bool> ChatExists(string chatId)
        {
            var filter = Builders<BsonDocument>.Filter.Eq("ChatId", chatId);
            var existing = await _chatCollection.Find(filter).FirstOrDefaultAsync();
            return existing != null;
        }


        public async Task<List<Chat>> GetChatsByCustomerId(string customerId)
        {
            try
            {
                var filter = Builders<BsonDocument>.Filter.Eq("CustomerId", customerId);
                var documents = await _chatCollection.Find(filter).ToListAsync();

                return documents
                    .Select(doc => MongoDB.Bson.Serialization.BsonSerializer.Deserialize<Chat>(doc))
                    .ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine("GetChatsByCustomerId failed: " + ex.Message);
                return new List<Chat>();
            }
        }

        public async Task<Chat> GetChatById(string customerId, string chatId)
        {
            try
            {
                var filter = Builders<BsonDocument>.Filter.And(
                    Builders<BsonDocument>.Filter.Eq("CustomerId", customerId),
                    Builders<BsonDocument>.Filter.Eq("_id", ObjectId.Parse(chatId))
                );

                var doc = await _chatCollection.Find(filter).FirstOrDefaultAsync();
                return doc != null
                    ? MongoDB.Bson.Serialization.BsonSerializer.Deserialize<Chat>(doc)
                    : null;
            }
            catch (Exception ex)
            {
                Console.WriteLine("GetChatById failed: " + ex.Message);
                return null;
            }
        }

        public async Task AddMessagesToChat(string chatId, List<ChatMessage> messages)
        {
            try
            {
                var filter = Builders<BsonDocument>.Filter.Eq("_id", ObjectId.Parse(chatId));
                var update = Builders<BsonDocument>.Update.PushEach("Messages", messages.Select(m => m.ToBsonDocument()));
                var result = await _chatCollection.UpdateOneAsync(filter, update);

                if (result.ModifiedCount == 0)
                    throw new Exception("Failed to add messages to chat");
            }
            catch (Exception ex)
            {
                Console.WriteLine("AddMessagesToChat failed: " + ex.Message);
            }
        }
    }
}
