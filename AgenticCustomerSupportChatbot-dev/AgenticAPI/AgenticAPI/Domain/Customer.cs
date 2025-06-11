using MongoDB.Bson.Serialization.Attributes;

namespace AgenticAPI.Domain
{
    [BsonIgnoreExtraElements]
    public class Customer
    {
        public string? CustomerId { get; set; }
        public string? CustomerName { get; set; }
        public string? PaymentMethod { get; set; }
        public DateTime? CreatedOn { get; set; }
        public DateTime? NextPayment { get; set; }
        public DateTime? FinalPayment { get; set; }
        public Address? Address { get; set; }
        public string? EmailAddress { get; set; }
        public PhoneInfo? PhoneInfo { get; set; }
        public bool? PaymentReminder { get; set; }
        public List<String> Notes { get; set; } = new List<String>();
    }
}
