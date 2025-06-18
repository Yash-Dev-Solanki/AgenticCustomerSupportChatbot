using System.ComponentModel.DataAnnotations;
using AgenticAPI.Domain;
using MediatR;

namespace AgenticAPI.Application.UpdateCustomer
{
    public class UpdateCustomerRequestModel: IRequest<UpdateCustomerResponseModel>
    {
        [Required]
        public string? CustomerId { get; set; }
        [Required]
        public string? updatedField { get; set; }
        [Required]
        public object? updatedValue { get; set; }
    }
}
