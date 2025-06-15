using AgenticAPI.Infrastructure;
using AgenticAPI.Application.GetChatById;

namespace AgenticAPI.Application.GetChatById
{
    public class GetChatByIdCommand
    {
        private readonly IChatService _chatService;

        public GetChatByIdCommand(IChatService chatService)
        {
            _chatService = chatService;
        }

        public async Task<GetChatByIdResponseModel?> ExecuteAsync(string customerId, string chatId)
        {
            var chat = await _chatService.GetChatById(customerId, chatId);
            if (chat == null)
                return null;

            return new GetChatByIdResponseModel
            {
                ChatId = chat.ChatId,
                CustomerId = chat.CustomerId,
                CreatedAt = chat.CreatedAt,
                Messages = chat.Messages.Select(m => new GetChatByIdResponseModel.ChatMessageModel
                {
                    Sender = m.Sender,
                    Message = m.Message,
                    Timestamp = m.Timestamp
                }).ToList()
            };
        }
    }
}
