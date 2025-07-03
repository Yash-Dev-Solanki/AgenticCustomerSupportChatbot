using System;
using MongoDB.Bson;
using MongoDB.Driver;
using AgenticAPI.Domain;
using MongoDB.Bson.Serialization;


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
        
        public async Task<List<ChatSummary>> GetChatsByCustomerId(string customerId)
        {
            try
            {
                var filter = Builders<BsonDocument>.Filter.Eq("CustomerId", customerId);
                var projection = Builders<BsonDocument>.Projection
                    .Include("ChatId")
                    .Include("ChatTitle")
                    .Include("CreatedAt");
                var documents = await _chatCollection.Find(filter).Project(projection).ToListAsync();

                var result = documents.Select(doc => new ChatSummary
                {
                    ChatId = doc.GetValue("ChatId", BsonNull.Value).AsString,
                    ChatTitle = doc.GetValue("ChatTitle", BsonNull.Value).AsString,
                    CreatedAt = doc.GetValue("CreatedAt", BsonNull.Value).ToUniversalTime()
                }).ToList();

                return result;
            }
            catch (Exception ex)
            {
                Console.WriteLine("GetChatsByCustomerId failed: " + ex.Message);
                return new List<ChatSummary>();
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

        public async Task<Chat?> UpdateChatDetails(string chatId, string fieldToUpdate, object newValue)
        {
            try
            {
                var filter = Builders<BsonDocument>.Filter.Eq("ChatId", chatId);
                var chat = await _chatCollection.Find(filter).FirstOrDefaultAsync();

                if (chat == null)
                {
                    throw new ArgumentException("ChatId could not be found");
                }

                chat[fieldToUpdate] = BsonValue.Create(newValue);
                await _chatCollection.ReplaceOneAsync(filter, chat);
                return BsonSerializer.Deserialize<Chat>(chat);
            }
            catch (ArgumentException)
            {
                throw;
            }
            catch (Exception ex)
            {
                Console.WriteLine("Failed to Update Chat Details: " + ex.Message);
                throw new Exception(ex.Message, ex);
            }
        }
    }
}
