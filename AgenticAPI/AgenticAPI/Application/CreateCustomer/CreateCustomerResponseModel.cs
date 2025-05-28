using AgenticAPI.Domain;
using System;
using System.Net;

namespace AgenticAPI.Application.CreateCustomer
{
    public class CreateCustomerResponseModel: BaseResponseModel
    {
        public string? CustomerId { get; set; }

        public string ResponseDescription
        {
            get
            {
                if (StatusCode == HttpStatusCode.Created)
                {
                    return $"Customer created with Customer Id {CustomerId}";
                }
                else if (StatusCode == HttpStatusCode.BadRequest)
                {
                    return $"Could not create customer due to: {Errors!.ToString()}";
                }
                else
                {
                    return "Internal Server Error";
                }
            }
        }

        public CreateCustomerResponseModel(): base()
        {

        }
    }
}
