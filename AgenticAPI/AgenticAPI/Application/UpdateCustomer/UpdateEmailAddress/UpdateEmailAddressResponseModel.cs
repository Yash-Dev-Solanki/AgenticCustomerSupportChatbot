using System.ComponentModel.DataAnnotations;
using AgenticAPI.Domain;

namespace AgenticAPI.Application.UpdateCustomer.UpdateEmailAddress
{
    public class UpdateEmailAddressResponseModel: BaseResponseModel
    {
        public Customer? Customer { get; set; }

        public UpdateEmailAddressResponseModel() : base()
        {
        }
    }
}
