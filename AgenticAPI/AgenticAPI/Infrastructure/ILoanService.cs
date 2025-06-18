using System.Collections.Generic;
using System.Threading.Tasks;
using MongoDB.Driver;
using MongoDB.Bson;
using AgenticAPI.Domain;

namespace AgenticAPI.Infrastructure
{
    public interface ILoanService
    {
        public Task<LoanDetails?> GetLoanDetailsByCustomerId(string customerId);
        public Task<List<LoanPayment>> GetPaymentsByLoanAccount(string loanAccountNumber);
        public Task<bool> AddLoanDetails(LoanDetails loanDetails);
        public Task<bool> AddLoanPayment(LoanPayment loanPayment);
    }
}
