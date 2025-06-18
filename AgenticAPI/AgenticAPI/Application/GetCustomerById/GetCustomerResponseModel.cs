using AgenticAPI.Domain;

namespace AgenticAPI.Application.GetCustomerById
{
    public class GetCustomerResponseModel: BaseResponseModel
    {
        public Customer? Customer { get; set; }
    }
}
