using AgenticAPI.Infrastructure;
using AgenticAPI.Domain;

namespace AgenticAPI.Application.StoreChatMessage
{
    public class StoreChatMessagesCommand
    {
        private readonly IChatService _chatService;

        public StoreChatMessagesCommand(IChatService chatService)
        {
            _chatService = chatService;
        }

        public async Task<StoreChatMessagesResponseModel> ExecuteAsync(StoreChatMessagesRequestModel request)
        {
            var messages = request.Messages.Select(msg => new ChatMessage
            {
                Sender = msg.Sender,
                Message = msg.Message,
                Timestamp = msg.Timestamp == default ? DateTime.UtcNow : msg.Timestamp
            }).ToList();

            await _chatService.AddMessagesToChat(request.ChatId, messages);

            return new StoreChatMessagesResponseModel
            {
                Success = true,
                Message = $"{messages.Count} message(s) stored successfully."
            };
        }
    }
}
