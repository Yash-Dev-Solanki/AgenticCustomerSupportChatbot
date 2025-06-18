using Microsoft.AspNetCore.Mvc;
using AgenticAPI.Infrastructure;
using AgenticAPI.Application.StoreChatMessage;
using AgenticAPI.Domain;
using AgenticAPI.Application.CreateChat;

namespace AgenticAPI.WebAPI.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ChatController : ControllerBase
    {
        private readonly IChatService _chatService;

        public ChatController(IChatService chatService)
        {
            _chatService = chatService;
        }
        [HttpPost("create-chat")]
        public async Task<IActionResult> CreateChat([FromBody] CreateChatRequestModel request)
        {
            try
            {
                var command = new CreateChatCommand(_chatService);
                var result = await command.ExecuteAsync(request);
                return CreatedAtAction(nameof(GetChatById), new { customerId = request.CustomerId, chatId = result.ChatId }, result);
            }
            catch (Exception ex)
            {
                return StatusCode(500, ex.Message);
            }
        }

        [HttpGet("{customerId}")]
        public async Task<IActionResult> GetChatsByCustomerId(string customerId)
        {
            var chats = await _chatService.GetChatsByCustomerId(customerId);
            if (chats == null || chats.Count == 0)
                return NotFound($"No chats found for customerId: {customerId}");
            return Ok(chats);
        }
        [HttpGet("{customerId}/{chatId}")]
        public async Task<IActionResult> GetChatById(string customerId, string chatId)
        {
            var chat = await _chatService.GetChatById(customerId, chatId);
            if (chat == null)
                return NotFound($"Chat with id {chatId} for customerId {customerId} not found");
            return Ok(chat);
        }
        [HttpPost("store-messages")]
        public async Task<IActionResult> AddMessagesToChat([FromBody] StoreChatMessagesRequestModel request)
        {
            await _chatService.AddMessagesToChat(request.ChatId, request.Messages);
            return Ok($"{request.Messages.Count} messages added");
        }
    }
}
