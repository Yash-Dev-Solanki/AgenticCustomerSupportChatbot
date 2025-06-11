using MongoDB.Driver;
using MongoDB.Bson;
using AgenticAPI.Domain;

namespace AgenticAPI.Infrastructure
{
    public interface IMongoService
    {
        public Task<bool> AddCustomer(Customer customer);
        public Task<BsonDocument?> GetCustomerByID(string customerId);
        public Task<BsonDocument?> UpdateCustomer(string customerId, string fieldName, object newValue);
    }
}
