using AgenticAPI.Domain;
using AgenticAPI.Infrastructure;
using MediatR;
using MongoDB.Bson.Serialization;
using System;
using System.Net;

namespace AgenticAPI.Application.UpdateCustomer
{
    public class UpdateCustomerCommand : IRequestHandler<UpdateCustomerRequestModel, UpdateCustomerResponseModel>
    {
        public IMongoService _mongoService;

        public UpdateCustomerCommand(IMongoService mongoService)
        {
            _mongoService = mongoService;
        }
        public async Task<UpdateCustomerResponseModel> Handle(UpdateCustomerRequestModel request, CancellationToken cancellationToken)
        {
            var response = new UpdateCustomerResponseModel();

            try
            {
                var result = await _mongoService.UpdateCustomer(request.CustomerId!, request.updatedField!, request.updatedValue!);

                response.Customer = BsonSerializer.Deserialize<Customer>(result);
                response.StatusCode = HttpStatusCode.Accepted;
            }
            catch (ArgumentOutOfRangeException ex)
            {
                response.Success = false;
                response.StatusCode = HttpStatusCode.BadRequest;
                response.Errors!.Add(ex.Message);
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
