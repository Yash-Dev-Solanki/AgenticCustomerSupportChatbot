using AgenticAPI.Domain;
using AgenticAPI.Infrastructure;
using MediatR;
using MongoDB.Bson.Serialization;
using System;
using System.Net;

namespace AgenticAPI.Application.UpdateCustomer.UpdateEmailAddress
{
    public class UpdateEmailAddressCommand : IRequestHandler<UpdateEmailAddressRequestModel, UpdateEmailAddressResponseModel>
    {
        public IMongoService _mongoService;

        public UpdateEmailAddressCommand(IMongoService mongoService)
        {
            _mongoService = mongoService;
        }
        public async Task<UpdateEmailAddressResponseModel> Handle(UpdateEmailAddressRequestModel request, CancellationToken cancellationToken)
        {
            var response = new UpdateEmailAddressResponseModel();

            try
            {
                var result = await _mongoService.UpdateCustomer(request.CustomerId!, "EmailAddress", request.EmailAddress!);

                response.Customer = BsonSerializer.Deserialize<Customer>(result);
                response.StatusCode = HttpStatusCode.Accepted;
            }
            catch (ArgumentOutOfRangeException)
            {
                response.Success = false;
                response.StatusCode = HttpStatusCode.BadRequest;
                response.Errors!.Add("Customer Id not found");
            }
            catch (Exception ex)
            {
                response.Success = false;
                response.StatusCode = HttpStatusCode.InternalServerError;
                response.Errors!.Add($"DB could not be accessed:  {ex.Message}");
            }

            return response;
        }
    }
}
