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
                var loanDetails = await GetLoanDetailsByCustomerId(loanPayment.CustomerId);
                if (loanDetails == null)
                {
                    throw new Exception($"No loan details found for customer ID: {loanPayment.CustomerId}");
                }

                double monthlyRate = loanDetails.InterestRate / 12 / 100;
                var filter = Builders<LoanPayment>.Filter.Eq(lp => lp.CustomerId, loanPayment.CustomerId);
                var latestPayment = await _loanPaymentsCollection
                    .Find(filter)
                    .SortByDescending(lp => lp.PaymentDate)
                    .Limit(1)
                    .FirstOrDefaultAsync();

                double previousPrincipal = latestPayment?.CurrentPrincipal ?? loanDetails.LoanAmount;
                double interest = Math.Round(previousPrincipal * monthlyRate, 2);
                double principalPaid = Math.Round(loanPayment.PaymentAmount - interest, 2);
                double currentPrincipal = Math.Round(previousPrincipal - principalPaid, 2);
                var loanPaymentResult = new LoanPayment
                {
                    CustomerId = loanPayment.CustomerId,
                    LoanAccountNumber = loanPayment.LoanAccountNumber,
                    PaymentDate = loanPayment.PaymentDate,
                    PaymentAmount = loanPayment.PaymentAmount,
                    PaymentMode = loanPayment.PaymentMode,
                    TransactionId = loanPayment.TransactionId,
                    PreviousPrincipal = previousPrincipal,
                    InterestPaid = interest,
                    PrincipalPaid = principalPaid,
                    CurrentPrincipal = currentPrincipal
                };
                await _loanPaymentsCollection.InsertOneAsync(loanPaymentResult);
                return true;
            }
            catch (Exception ex)
            {
                throw new Exception("Error adding loan payment with computed fields: " + ex.Message);
            }
        }

    }
}
