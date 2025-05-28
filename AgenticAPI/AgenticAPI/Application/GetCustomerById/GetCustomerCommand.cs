using AgenticAPI.Domain;
using AgenticAPI.Infrastructure;
using MediatR;
using MongoDB.Bson.Serialization;
using System;
using System.Net;

namespace AgenticAPI.Application.GetCustomerById
{
    public class GetCustomerCommand: IRequestHandler<GetCustomerRawRequestModel, GetCustomerResponseModel>
    {
        public IMongoService _mongoService;

        public GetCustomerCommand(IMongoService mongoService)
        {
            _mongoService = mongoService;
        }

        public async Task<GetCustomerResponseModel> Handle(GetCustomerRawRequestModel request, CancellationToken cancellationToken)
        {
            var response = new GetCustomerResponseModel();
            try
            {
                Console.WriteLine($"Fetching {request.CustomerId}");
                var searchResult = await _mongoService.GetCustomerById(request.CustomerId!);

                if (searchResult == null)
                {
                    response.Success = false;
                    response.StatusCode = HttpStatusCode.BadRequest;
                    response.Errors!.Add("Customer Id not found in accounts collection");
                } 
                else
                {
                    response.Customer = BsonSerializer.Deserialize<Customer>(searchResult);
                    response.StatusCode = HttpStatusCode.OK;
                }
            }
            catch (Exception ex)
            {
                response.Success = false;
                response.StatusCode = HttpStatusCode.InternalServerError;
                response.Errors!.Add(ex.Message);
            }
            
            return response;
        }
    }
}
