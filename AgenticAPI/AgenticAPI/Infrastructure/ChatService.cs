using System;
using MongoDB.Bson;
using MongoDB.Driver;
using AgenticAPI.Domain;


namespace AgenticAPI.Infrastructure
{
    public class ChatService : IChatService
    {
        private readonly IMongoCollection<BsonDocument> _chatCollection;

        public ChatService(IConfiguration configuration, IMongoService accountsCollection)
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
        
        public async Task<List<string>> GetChatsByCustomerId(string customerId)
        {
            try
            {
                var filter = Builders<BsonDocument>.Filter.Eq("CustomerId", customerId);
                var projection = Builders<BsonDocument>.Projection
                    .Include("ChatId");
                var documents = await _chatCollection.Find(filter).Project(projection).ToListAsync();

                return documents.Select(c => c["ChatId"].AsString).ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine("GetChatsByCustomerId failed: " + ex.Message);
                return new List<string>();
            }
        }


        public async Task<Chat?> GetByChatId(string chatId)
        {
            try
            {
                var filter = Builders<BsonDocument>.Filter.Eq("ChatId", chatId);
                var doc = await _chatCollection.Find(filter).FirstOrDefaultAsync();
                Console.WriteLine(doc);
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


        public async Task<bool> AddMessagesToChat(string chatId, List<ChatMessage> messages)
        {
            try
            {
                var filter = Builders<BsonDocument>.Filter.Eq("ChatId", chatId);
                var update = Builders<BsonDocument>.Update.PushEach("Messages", messages.Select(m => m.ToBsonDocument()));
                var result = await _chatCollection.UpdateOneAsync(filter, update);

                if (result.MatchedCount == 0)
                {
                    throw new ArgumentException("Chat Id not found in Mongo DB");
                }

                return result.ModifiedCount > 0;
            }
            catch (ArgumentException)
            {
                throw;
            }
            catch (Exception ex)
            {
                Console.WriteLine("AddMessagesToChat failed: " + ex.Message);
                throw new Exception(ex.Message, ex);
            }
        }
    }
}
