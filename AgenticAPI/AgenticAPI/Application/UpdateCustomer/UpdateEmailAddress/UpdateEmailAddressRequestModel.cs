using System.ComponentModel.DataAnnotations;
using AgenticAPI.Domain;
using MediatR;

namespace AgenticAPI.Application.UpdateCustomer.UpdateEmailAddress
{
    public class UpdateEmailAddressRequestModel: IRequest<UpdateEmailAddressResponseModel>
    {
        [Required]
        public string? CustomerId { get; set; }

        [Required]
        public string? EmailAddress { get; set; }
    }
}
