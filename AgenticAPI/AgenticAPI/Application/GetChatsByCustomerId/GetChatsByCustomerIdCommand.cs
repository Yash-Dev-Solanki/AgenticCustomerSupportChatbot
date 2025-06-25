using AgenticAPI.Infrastructure;
using AgenticAPI.Application.GetChatsByCustomerId;
using MediatR;

namespace AgenticAPI.Application.GetChatsByCustomerId
{
    public class GetChatsByCustomerIdCommand: IRequestHandler<GetChatsByCustomerIdRequestModel, GetChatsByCustomerIdResponseModel>
    {
        private readonly IChatService _chatService;

        public GetChatsByCustomerIdCommand(IChatService chatService)
        {
            _chatService = chatService;
        }

        public async Task<GetChatsByCustomerIdResponseModel> Handle(GetChatsByCustomerIdRequestModel request, CancellationToken cancellationToken)
        {
            var response = new GetChatsByCustomerIdResponseModel();
            try
            {
                var result = await _chatService.GetChatsByCustomerId(request.CustomerId!);
                response.Success = true;
                if (result == null || result.Count == 0)
                {
                    response.StatusCode = System.Net.HttpStatusCode.NotFound;
                    response.Errors.Add("Customer Id has no related chats");
                }
                else
                {
                    response.StatusCode = System.Net.HttpStatusCode.OK;
                    response.ChatIds = result;
                } 
            }
            catch (Exception ex)
            {
                response.Success = false;
                response.StatusCode= System.Net.HttpStatusCode.InternalServerError;
                response.Errors!.Add(ex.Message);
            }

            return response;
        }
    }
}
