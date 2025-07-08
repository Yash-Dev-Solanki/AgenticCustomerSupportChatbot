using Microsoft.AspNetCore.Mvc;
using AgenticAPI.Infrastructure;
using AgenticAPI.Application.AddChatMessage;
using AgenticAPI.Domain;
using AgenticAPI.Application.CreateChat;
using MediatR;
using System.ComponentModel.DataAnnotations;
using AgenticAPI.Application.GetChatById;
using AgenticAPI.Application.GetChatsByCustomerId;
using AgenticAPI.Application.UpdateChatSummary;

namespace AgenticAPI.WebAPI.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ChatController : ControllerBase
    {
        private readonly IChatService _chatService;
        private readonly IMediator _mediator;

        public ChatController(IChatService chatService, IMediator mediator)
        {
            _chatService = chatService;
            _mediator = mediator;
        }


        [HttpPost("CreateChat")]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [ActionName("CreateChat")]
        public async Task<IActionResult> CreateChat([FromHeader][Required] string customerId, [FromHeader][Required] string chatTitle)
        {
            try
            {
                var request = new CreateChatRequestModel { CustomerId = customerId, ChatTitle = chatTitle };
                var response = await _mediator.Send(request);

                if (response.StatusCode == System.Net.HttpStatusCode.Created)
                {
                    return Created("Chat Created for Customer", response);
                }
                else if (response.StatusCode == System.Net.HttpStatusCode.BadRequest)
                {
                    return BadRequest(response);
                }
                else
                {
                    return StatusCode(500, "Could not access DB");
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, ex.Message);
            }
        }


        [HttpPost("AddMessages")]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [ActionName("AddMessages")]
        public async Task<IActionResult> AddMessagesToChat([FromBody] AddChatMessagesRequestModel request)
        {
            try
            {
                var response = await _mediator.Send(request);
                
                if (response.StatusCode == System.Net.HttpStatusCode.Created)
                {
                    return Created($"{request.Messages?.Count} added to Chat History", response);
                }
                else if (response.StatusCode == System.Net.HttpStatusCode.BadRequest)
                {
                    return BadRequest(response);
                }
                else
                {
                    return StatusCode(500, "Could not access DB");
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, ex.Message);
            }
        }

        [HttpGet("GetChatsForCustomer")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> GetChatsByCustomerId([FromHeader][Required] string customerId)
        {
            try
            {
                var request = new GetChatsByCustomerIdRequestModel { CustomerId = customerId };
                var response = await _mediator.Send(request);

                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    return NotFound(response);
                }
                else if (response.StatusCode == System.Net.HttpStatusCode.OK)
                {
                    return Ok(response);
                }
                else
                {
                    return StatusCode(500, "Could not access DB");
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, ex.Message);
            }
        }


        [HttpGet("{chatId}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [ActionName("GetChatById")]
        public async Task<IActionResult> GetChatById(string chatId)
        {
            try
            {
                var request = new GetChatByIdRequestModel { ChatId = chatId };
                var response = await _mediator.Send(request);

                if (response.StatusCode == System.Net.HttpStatusCode.OK)
                {
                    return Ok(response);
                }
                else if (response.StatusCode == System.Net.HttpStatusCode.BadRequest)
                {
                    return BadRequest(response);
                }
                else
                {
                    return StatusCode(500, "Could not access DB");
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, ex.Message);
            } 
        }

        [HttpPost("SetChatSummary")]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [ActionName("SetChatSummary")]
        public async Task<IActionResult> SetChatSummary([FromBody] UpdateChatSummaryRequestModel request)
        {
            try
            {
                var response = await _mediator.Send(request);

                if (response.StatusCode == System.Net.HttpStatusCode.Created)
                {
                    return Created("Chat Summary Set: ", response);
                }
                else if (response.StatusCode == System.Net.HttpStatusCode.BadRequest)
                {
                    return BadRequest(response);
                }
                else
                {
                    return StatusCode(500, "Could not access DB");
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, ex.Message);
            }
        }
    }
}
