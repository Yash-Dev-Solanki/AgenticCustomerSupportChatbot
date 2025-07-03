using System;
using System.Collections.Generic;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace AgenticAPI.Domain
{
    [BsonIgnoreExtraElements]
    public class LoanDetails
    {
        [BsonId]
        [BsonRepresentation(BsonType.ObjectId)]
        public string Id { get; set; }
        public string CustomerId { get; set; }
        public string LoanAccountNumber { get; set; }
        public double LoanAmount { get; set; }
        public double InterestRate { get; set; }
        public int TenureMonths { get; set; }
        public double EmiAmount { get; set; }
        public DateTime StartDate { get; set; }
        public string Status { get; set; }
    }
}
