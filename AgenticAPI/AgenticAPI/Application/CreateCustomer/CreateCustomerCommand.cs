using System;
using System.Net;
using AgenticAPI.Domain;
using AgenticAPI.Infrastructure;
using AutoMapper;
using MediatR;

namespace AgenticAPI.Application.CreateCustomer
{
    public class CreateCustomerCommand: IRequestHandler<CreateCustomerRawRequestModel, CreateCustomerResponseModel>
    {
        public IMapper _mapper;
        public IMongoService _mongoService;

        public CreateCustomerCommand(IMapper mapper, IMongoService mongoService)
        {
            _mapper = mapper;
            _mongoService = mongoService;
        }

        public async Task<CreateCustomerResponseModel> Handle(CreateCustomerRawRequestModel request, CancellationToken cancellationToken)
        {
            Customer customer = _mapper.Map<Customer>(request);
            customer.CustomerId = Guid.NewGuid().ToString();
            customer.Notes = new List<string>();
            customer.Notes.Add($"Customer created successfully at {customer.CreatedOn}");
            var result = await _mongoService.AddCustomer(customer);

            var response = new CreateCustomerResponseModel();
            response.CustomerId = customer.CustomerId;
            response.Errors = new List<string>();

            if (result == false)
            {
                response.Errors.Add("Mongo DB could not be accessed");
                response.Success = false;
                response.StatusCode = HttpStatusCode.InternalServerError;
            }
            else
            {
                response.StatusCode = HttpStatusCode.Created;
            }

                return response;
        }
    }
}
