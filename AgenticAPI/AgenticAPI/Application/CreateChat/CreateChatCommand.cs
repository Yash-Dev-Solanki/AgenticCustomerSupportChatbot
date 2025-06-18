using AgenticAPI.Domain;
using AgenticAPI.Infrastructure;
using MongoDB.Bson;

namespace AgenticAPI.Application.CreateChat
{
    public class CreateChatCommand
    {
        private readonly IChatService _chatService;

        public CreateChatCommand(IChatService chatService)
        {
            _chatService = chatService;
        }

        public async Task<CreateChatResponseModel> ExecuteAsync(CreateChatRequestModel request)
        {
            string uniqueChatId;

            // Keep generating until a unique one is found
            do
            {
                uniqueChatId = ObjectId.GenerateNewId().ToString();
            } while (await _chatService.ChatExists(uniqueChatId));

            var newChat = new Chat
            {
                ChatId = uniqueChatId,
                CustomerId = request.CustomerId,
                CreatedAt = DateTime.UtcNow,
                Messages = new List<ChatMessage>()
            };

            var success = await _chatService.CreateChat(newChat);

            if (!success)
            {
                throw new Exception("Failed to create chat session.");
            }

            return new CreateChatResponseModel
            {
                ChatId = newChat.ChatId,
                CreatedAt = newChat.CreatedAt,
                Message = "Chat session created successfully."
            };
        }
    }
}
