using System.ComponentModel.DataAnnotations;
using AgenticAPI.Domain;
using MediatR;

namespace AgenticAPI.Application.GetCustomerById
{
    public class GetCustomerRawRequestModel: IRequest<GetCustomerResponseModel>
    {
        [Required]
        public string? CustomerId;
    }
}
