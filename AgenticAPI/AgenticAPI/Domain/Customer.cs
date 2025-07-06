using MongoDB.Bson.Serialization.Attributes;

namespace AgenticAPI.Domain
{
    [BsonIgnoreExtraElements]
    public class Customer
    {
        public string? CustomerId { get; set; }
        public string? SSN { get; set; }
        public string? CustomerName { get; set; }
        public DateTime? CreatedOn { get; set; }
        public Address? Address { get; set; }
        public string? EmailAddress { get; set; }
        public PhoneInfo? PhoneInfo { get; set; }
        public bool? PaymentReminder { get; set; }
    }
}
