using AgenticAPI.Domain;
using AgenticAPI.Infrastructure;
using MediatR;
using MongoDB.Bson;

namespace AgenticAPI.Application.CreateChat
{
    public class CreateChatCommand: IRequestHandler<CreateChatRequestModel, CreateChatResponseModel>
    {
        private readonly IChatService _chatService;
        private readonly IMongoService _accountsService;

        public CreateChatCommand(IChatService chatService, IMongoService accountsService)
        {
            _chatService = chatService;
            _accountsService = accountsService;
        }

        public async Task<CreateChatResponseModel> Handle(CreateChatRequestModel request, CancellationToken cancellationToken)
        {
            var response = new CreateChatResponseModel();

            try
            {
                // Check if custmer Id is valid
                bool validCustomerId = await _accountsService.CheckCustomerExists(request.CustomerId);
                if (!validCustomerId)
                {
                    response.Success = true;
                    response.StatusCode = System.Net.HttpStatusCode.BadRequest;
                    response.Errors!.Add("Customer Id not present in accounts collection");
                    return response;
                }

                // Using GUID as a Chat ID & casting to string
                var newChat = new Chat
                {
                    ChatId = Guid.NewGuid().ToString(),
                    CustomerId = request.CustomerId,
                    CreatedAt = DateTime.UtcNow,
                    Messages = new List<ChatMessage>()
                };

                var success = await _chatService.CreateChat(newChat);
                if (success)
                {
                    response.Success = true;
                    response.StatusCode = System.Net.HttpStatusCode.Created;
                    response.ChatId = newChat.ChatId;
                    response.CreatedAt = newChat.CreatedAt;
                }
                else
                {
                    response.Success = false;
                    response.StatusCode = System.Net.HttpStatusCode.InternalServerError;
                    response.Errors!.Add("Mongo Write Exception Occured");
                }
            }
            catch (Exception ex)
            {
                response.Success = false;
                response.StatusCode = System.Net.HttpStatusCode.InternalServerError;
                response.Errors.Add(ex.Message);
            }
            
            return response;
        }
    }
}
