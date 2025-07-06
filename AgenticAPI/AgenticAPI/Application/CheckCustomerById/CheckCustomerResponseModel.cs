using AgenticAPI.Domain;

namespace AgenticAPI.Application.CheckCustomerById
{
    public class CheckCustomerResponseModel: BaseResponseModel
    {
        public bool CustomerExists { get; set; }
        public string? CustomerId { get; set; }

        public CheckCustomerResponseModel(): base()
        {
        }
    }
}
