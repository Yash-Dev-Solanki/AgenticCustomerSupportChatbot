using AgenticAPI.Domain;
using MediatR;

namespace AgenticAPI.Application.CreateCustomer
{
    public class CreateCustomerRawRequestModel: IRequest<CreateCustomerResponseModel>
    {
        public string? SSN { get; set; }
        public string? CustomerName { get; set; }
        public DateTime? CreatedOn { get; set; }
        public Address? Address { get; set; }
        public PhoneInfo? PhoneInfo { get; set; }
        public string? EmailAddress { get; set; }
        public bool? PaymentReminder { get; set; }
    }
}
