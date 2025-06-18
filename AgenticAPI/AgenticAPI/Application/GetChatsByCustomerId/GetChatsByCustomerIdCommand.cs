using AgenticAPI.Infrastructure;
using AgenticAPI.Application.GetChatsByCustomerId;

namespace AgenticAPI.Application.GetChatsByCustomerId
{
    public class GetChatsByCustomerIdCommand
    {
        private readonly IChatService _chatService;

        public GetChatsByCustomerIdCommand(IChatService chatService)
        {
            _chatService = chatService;
        }

        public async Task<List<GetChatsByCustomerIdResponseModel>> ExecuteAsync(string customerId)
        {
            var chats = await _chatService.GetChatsByCustomerId(customerId);

            return chats.Select(chat => new GetChatsByCustomerIdResponseModel
            {
                ChatId = chat.ChatId,
                CustomerId = chat.CustomerId,
                CreatedAt = chat.CreatedAt,
            }).ToList();
        }
    }
}
