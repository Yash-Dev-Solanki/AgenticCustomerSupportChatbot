using AgenticAPI.Infrastructure;
using MediatR;

namespace AgenticAPI.Application.CheckCustomerById
{
    public class CheckCustomerCommand : IRequestHandler<CheckCustomerRequestModel, CheckCustomerResponseModel>
    {
        private readonly IMongoService _mongoService;

        public CheckCustomerCommand(IMongoService mongoService)
        {
            _mongoService = mongoService;
        }

        public async Task<CheckCustomerResponseModel> Handle(CheckCustomerRequestModel request, CancellationToken cancellationToken)
        {
            var response = new CheckCustomerResponseModel();
            try
            {
                var result = await _mongoService.CheckCustomerExists(request.CustomerId);

                if (result == true)
                {
                    response.Success = true;
                    response.StatusCode = System.Net.HttpStatusCode.OK;
                    response.CustomerExists = true;
                }
                else
                {
                    response.Success = true;
                    response.StatusCode = System.Net.HttpStatusCode.NotFound;
                    response.CustomerExists = false;
                }
            }
            catch (Exception ex)
            {
                response.Success = false;
                response.StatusCode = System.Net.HttpStatusCode.InternalServerError;
                response.Errors!.Add(ex.Message);
            }

            return response;
        }
    }
}
