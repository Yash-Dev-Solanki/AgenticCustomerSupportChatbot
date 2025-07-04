using AgenticAPI.Infrastructure;
using AgenticAPI.Domain;
using MediatR;

namespace AgenticAPI.Application.AddChatMessage
{
    public class AddChatMessagesCommand: IRequestHandler<AddChatMessagesRequestModel, AddChatMessagesResponseModel>
    {
        private readonly IChatService _chatService;

        public AddChatMessagesCommand(IChatService chatService)
        {
            _chatService = chatService;
        }

        public async Task<AddChatMessagesResponseModel> Handle(AddChatMessagesRequestModel request, CancellationToken cancellationToken)
        {
            var response = new AddChatMessagesResponseModel();

            try
            {
                // Messages should be non-empty list
                if (request.Messages == null || request.Messages.Count == 0)
                {
                    response.Success = false;
                    response.StatusCode = System.Net.HttpStatusCode.BadRequest;
                    response.Errors!.Add("Messages cannot be empty");
                }
                var messages = request.Messages!.Select(msg => new ChatMessage
                {
                    Role = msg.Role,
                    Message = msg.Message,
                    Timestamp = msg.Timestamp == default ? DateTime.UtcNow : msg.Timestamp
                }).ToList();

                await _chatService.AddMessagesToChat(request.ChatId!, messages);

                response.Success = true;
                response.StatusCode = System.Net.HttpStatusCode.Created;
                response.Message = $"{messages.Count} messages added to history";
            }
            catch (ArgumentException)
            {
                response.Success = false;
                response.Errors!.Add("Chat Id not found in DB");
                response.StatusCode = System.Net.HttpStatusCode.BadRequest;
            }
            catch (Exception ex)
            {
                response.Success = false;
                response.Errors!.Add(ex.Message);
                response.StatusCode = System.Net.HttpStatusCode.InternalServerError;
            }

            return response;
        }
    }
}
