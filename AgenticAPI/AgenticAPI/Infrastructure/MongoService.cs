﻿using AgenticAPI.Domain;
using MongoDB.Bson;
using MongoDB.Driver;

namespace AgenticAPI.Infrastructure
{
    public class MongoService: IMongoService
    {
        IMongoCollection<BsonDocument> _accountsCollection;
        public MongoService(IConfiguration configuration) 
        {
            try
            {
                var connectionString = configuration["MongoSettings:ConnectionString"];
                var database = configuration["MongoSettings:Database"];
                var collection = configuration["MongoSettings:Collection"];

                var client = new MongoClient(connectionString);
                _accountsCollection = client.GetDatabase(database)
                    .GetCollection<BsonDocument>(collection);
            }
            catch (Exception ex)
            {
                throw new Exception(ex.StackTrace);
            }
        }

        public async Task<BsonDocument?> GetCustomerByID(string customerId)
        {
            try
            {
                var filter = Builders<BsonDocument>.Filter.Eq("CustomerId", customerId);
                var document = await _accountsCollection.Find(filter).FirstOrDefaultAsync();

                return document;
            }
            catch (Exception ex)
            {
                throw new Exception(ex.StackTrace);
            }
        }

        public async Task<bool> AddCustomer(Customer customer)
        {
            try
            {
                var toInsert = customer.ToBsonDocument();
                await _accountsCollection.InsertOneAsync(toInsert);
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.StackTrace);
                return false;
            }
        }

        public async Task<BsonDocument?> UpdateCustomer(string customerId, string fieldName, object newValue)
        {
            try
            {
                var customer = await GetCustomerByID(customerId);
                if (customer == null)
                {
                    throw new ArgumentOutOfRangeException("Customer Id Not found");
                }

                customer[fieldName] = BsonValue.Create(newValue);
                
                var filter = Builders<BsonDocument>.Filter.Eq("CustomerId", customerId);
                await _accountsCollection.ReplaceOneAsync(filter, customer);
                return customer;
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }

        public async Task<string?> CheckCustomerExists(string? customerId, string? SSN)
        {
            try
            {
                var filter = Builders<BsonDocument>.Filter.Or(
                    Builders<BsonDocument>.Filter.Eq("CustomerId", customerId),
                    Builders<BsonDocument>.Filter.Eq("SSN", SSN)
                );
                var account = await _accountsCollection.Find(filter).FirstOrDefaultAsync();

                if (account != null)
                    return account["CustomerId"].AsString;
                else
                    return null;
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }
    }
}
