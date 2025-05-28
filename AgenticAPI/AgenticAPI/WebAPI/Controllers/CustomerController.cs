using System;
using System.Net;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using MediatR;
using AutoMapper;
using AgenticAPI.Infrastructure;
using Microsoft.AspNetCore.Http.HttpResults;
using AgenticAPI.Application.CreateCustomer;
using AgenticAPI.Application.GetCustomerById;
using AgenticAPI.Domain;
using AgenticAPI.Application.UpdateCustomer.UpdateEmailAddress;

namespace AgenticAPI.WebAPI.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class CustomerController : ControllerBase
    {
        public IMediator _mediator;
        public IMapper _mapper;
        public IMongoService _mongoService;
         
        public CustomerController(IMediator mediator, IMapper mapper, IMongoService mongoService)
        {
            _mediator = mediator;
            _mapper = mapper;
            _mongoService = mongoService;
        }

        [HttpPost]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [ActionName("CreateCustomer")]
        public async Task<IActionResult> Post([FromBody] CreateCustomerRawRequestModel request)
        {
            var response = await _mediator.Send(request);

            if (response.StatusCode == HttpStatusCode.Created)
            {
                return Created("Customer created", response);
            }
            else 
            {
                return StatusCode(500, "Could not access DB");
            }
        }

        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [ActionName("GetCustomerById")]
        public async Task<IActionResult> Get([FromHeader] string customerId)
        {
            var request = new GetCustomerRawRequestModel { CustomerId = customerId };
            var response = await _mediator.Send(request);

            if (response.StatusCode == HttpStatusCode.OK)
            {
                return Ok(response);
            }
            else if (response.StatusCode == HttpStatusCode.BadRequest)
            {
                return BadRequest(response);
            }
            else
            {
                return StatusCode(500, "Could not access DB");
            }
        }

        [HttpPost("UpdateEmail")]
        [ProducesResponseType(StatusCodes.Status202Accepted)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [ActionName("UpdateCustomerEmailAddress")]
        public async Task<IActionResult> UpdateEmail([FromHeader] string customerId, [FromHeader] string newEmailAddress)
        {
            var request = new UpdateEmailAddressRequestModel();
            request.CustomerId = customerId;
            request.EmailAddress = newEmailAddress;
            var response = await _mediator.Send(request);

            if (response.StatusCode == HttpStatusCode.Accepted)
            {
                return Accepted(response);
            }
            else if (response.StatusCode == HttpStatusCode.BadRequest)
            {
                return BadRequest(response);
            }
            else
            {
                return StatusCode(500, "Could not access DB");
            }
        }
    }
}
