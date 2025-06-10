using System.ComponentModel.DataAnnotations;
using AgenticAPI.Domain;

namespace AgenticAPI.Application.UpdateCustomer
{
    public class UpdateCustomerResponseModel: BaseResponseModel
    {
        public Customer? Customer { get; set; }

        public UpdateCustomerResponseModel() : base()
        {
        }
    }
}
