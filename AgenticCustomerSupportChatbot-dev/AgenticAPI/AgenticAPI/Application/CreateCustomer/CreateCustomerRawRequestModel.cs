using AgenticAPI.Domain;
using MediatR;

namespace AgenticAPI.Application.CreateCustomer
{
    public class CreateCustomerRawRequestModel: IRequest<CreateCustomerResponseModel>
    {
        public string? CustomerName { get; set; }
        public PaymentMethod PaymentMethod { get; set; }
        public DateTime? CreatedOn { get; set; }
        public DateTime? NextPayment { get; set; }
        public DateTime? FinalPayment { get; set; }
        public Address? Address { get; set; }
        public PhoneInfo? PhoneInfo { get; set; }
        public string? EmailAddress { get; set; }
        public bool? PaymentReminder { get; set; }
    }
}
