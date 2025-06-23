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
        public string LoanAccountNumber { get; set; }
        public DateTime PaymentDate { get; set; }
        public double AmountPaid { get; set; }
        public string PaymentMode { get; set; }
        public string Status { get; set; }
        public string TransactionId { get; set; }
    }
}
