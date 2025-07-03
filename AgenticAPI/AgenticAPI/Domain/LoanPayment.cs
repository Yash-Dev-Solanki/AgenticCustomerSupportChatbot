using System;
using System.Collections.Generic;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace AgenticAPI.Domain
{
    [BsonIgnoreExtraElements]
    public class LoanPayment
    {
        [BsonId]
        [BsonRepresentation(BsonType.ObjectId)]
        public string Id { get; set; }
        [BsonElement("customerId")]
        public string CustomerId { get; set; }
        public string LoanAccountNumber { get; set; }
        public DateTime PaymentDate { get; set; }
        public double PaymentAmount { get; set; }
        public double InterestPaid { get; set; }
        public double PrincipalPaid { get; set; }
        public double PreviousPrincipal { get; set; }
        public double CurrentPrincipal { get; set; }
        public string PaymentMode { get; set; }
        public string TransactionId { get; set; }
    }
}
