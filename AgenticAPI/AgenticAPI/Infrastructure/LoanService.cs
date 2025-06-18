using AgenticAPI.Domain;
using MongoDB.Bson;
using MongoDB.Driver;
using Microsoft.Extensions.Configuration;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace AgenticAPI.Infrastructure
{
    public class LoanService : ILoanService
    {
        private readonly IMongoCollection<LoanDetails> _loanDetailsCollection;
        private readonly IMongoCollection<LoanPayment> _loanPaymentsCollection;


        public LoanService(IConfiguration configuration)
        {
            try
            {
                var connectionString = configuration["MongoSettings:ConnectionString"];
                var databaseName = configuration["MongoSettings:Database"];

                var client = new MongoClient(connectionString);
                var database = client.GetDatabase(databaseName);

                _loanDetailsCollection = database.GetCollection<LoanDetails>("LoanDetails");
                _loanPaymentsCollection = database.GetCollection<LoanPayment>("LoanPayments");

            }
            catch (Exception ex)
            {
                throw new Exception("Error initializing MongoDB collections: " + ex.Message);
            }
        }

        public async Task<LoanDetails?> GetLoanDetailsByCustomerId(string customerId)
        {
            try
            {
                var filter = Builders<LoanDetails>.Filter.Eq(ld => ld.CustomerId, customerId);
                var loanDetails = await _loanDetailsCollection.Find(filter).FirstOrDefaultAsync();
                return loanDetails;
            }
            catch (Exception ex)
            {
                throw new Exception("Error fetching loan details: " + ex.Message);
            }
        }

        public async Task<List<LoanPayment>> GetPaymentsByLoanAccount(string loanAccountNumber)
        {
            try
            {
                var filter = Builders<LoanPayment>.Filter.Eq(lp => lp.LoanAccountNumber, loanAccountNumber);
                var payments = await _loanPaymentsCollection.Find(filter).ToListAsync();
                return payments;
            }
            catch (Exception ex)
            {
                throw new Exception("Error fetching loan payments: " + ex.Message);
            }
        }
        public async Task<bool> AddLoanDetails(LoanDetails loanDetails)
        {
            try
            {
                await _loanDetailsCollection.InsertOneAsync(loanDetails);
                return true;
            }
            catch (Exception ex)
            {
                throw new Exception("Error adding loan details: " + ex.Message);
            }
        }

        public async Task<bool> AddLoanPayment(LoanPayment loanPayment)
        {
            try
            {
                await _loanPaymentsCollection.InsertOneAsync(loanPayment);
                return true;
            }
            catch (Exception ex)
            {
                throw new Exception("Error adding loan payments: " + ex.Message);
            }
        }
    }
}
