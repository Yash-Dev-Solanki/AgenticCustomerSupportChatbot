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
using AgenticAPI.Application.UpdateCustomer;
using System.ComponentModel.DataAnnotations;
using MongoDB.Bson;
using AgenticAPI.Application.CheckCustomerById;

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
            try
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
            catch (Exception ex)
            {
                return StatusCode(500, new { error = "Internal Server Error", message = ex.StackTrace });
            }
        }

        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [ActionName("GetCustomerById")]
        public async Task<IActionResult> Get([FromHeader] [Required] string customerId)
        {
            try
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
            catch (Exception ex)
            {
                return StatusCode(500, new { error = "Internal Server Error", message = ex.StackTrace });
            }
        }

        [HttpGet("CheckCustomer")]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [ActionName("CheckCustomerExists")]
        public async Task<IActionResult> CheckCustomerExists([FromHeader] string? customerId, [FromHeader] string? SSN)
        {
            if (String.IsNullOrEmpty(customerId) && String.IsNullOrEmpty(SSN))
            {
                return BadRequest(new
                {
                    Errors = new List<string>
                    {
                        "Either CustomerId or SSN must be provided."
                    }
                });
            }
            
            try
            {
                var request = new CheckCustomerRequestModel { CustomerId = customerId, SSN = SSN };
                var response = await _mediator.Send(request);

                if (response.StatusCode == HttpStatusCode.OK)
                {
                    return Ok(response);
                }
                else if (response.StatusCode == HttpStatusCode.NotFound)
                {
                    return NotFound(response);
                }
                else
                {
                    return StatusCode(500, "Could not access DB");
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = "Internal Server Error", message = ex.StackTrace });
            }
        }

        [HttpGet("VerifyCustomer")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status401Unauthorized)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> VerifyCustomer([FromHeader][Required] string customerId, [FromHeader][Required] string phoneInfoLastFourDigits)
        {
            try
            {
                var request = new GetCustomerRawRequestModel { CustomerId = customerId };
                var response = await _mediator.Send(request);

                if (response.StatusCode == HttpStatusCode.BadRequest)
                {
                    return BadRequest(response);
                }

                string? extractedHomePhone = response?.Customer?.PhoneInfo?.GetExtractedHomePhone();
                string? extractedWorkPhone = response?.Customer?.PhoneInfo?.GetExtractedWorkPhone();

                bool isValid = (phoneInfoLastFourDigits == extractedHomePhone || phoneInfoLastFourDigits == extractedWorkPhone);
                if (isValid)
                {
                    return Ok(response);
                }
                else
                {
                    response.Customer = null;
                    response.StatusCode = HttpStatusCode.Unauthorized;
                    response.Success = false;
                    response.Errors.Add("Mismatch in phone info provided & phone info in DB");
                    return Unauthorized(response);
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = "Internal Server Error", message = ex.StackTrace });
            }
        }

        [HttpPost("UpdateEmail")]
        [ProducesResponseType(StatusCodes.Status202Accepted)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [ActionName("UpdateCustomerEmailAddress")]
        public async Task<IActionResult> UpdateEmail([FromHeader][Required] string customerId, [FromHeader][Required] string newEmailAddress)
        {
            try
            {
                var request = new UpdateCustomerRequestModel();
                request.CustomerId = customerId;
                request.updatedField = "EmailAddress";
                request.updatedValue = newEmailAddress;
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
            catch (Exception ex)
            {
                return StatusCode(500, new { error = "Internal Server Error", message = ex.StackTrace });
            }
        }

        [HttpPost("UpdatePaymentReminder")]
        [ProducesResponseType(StatusCodes.Status202Accepted)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [ActionName("CustomerPaymentReminder")]
        public async Task<IActionResult> UpdatePaymentReminder([FromHeader][Required] string customerId, [FromHeader][Required] bool newPaymentReminder)
        {
            try
            {
                var request = new UpdateCustomerRequestModel();
                request.CustomerId = customerId;
                request.updatedField = "PaymentReminder";
                request.updatedValue = newPaymentReminder;
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
            catch (Exception ex)
            {
                return StatusCode(500, new { error = "Internal Server Error", message = ex.StackTrace });
            }
        }

        [HttpPost("UpdatePhoneInfo")]
        [ProducesResponseType(StatusCodes.Status202Accepted)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [ActionName("CustomerPhoneInfo")]
        public async Task<IActionResult> UpdatePhoneInfo([FromHeader][Required] string customerId, [FromBody] PhoneInfo newPhoneInfo)
        {
            try
            {
                var request = new UpdateCustomerRequestModel();
                request.CustomerId = request.CustomerId = customerId;
                request.updatedField = "PhoneInfo";
                request.updatedValue = newPhoneInfo.ToBsonDocument();
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
            catch (Exception ex)
            {
                return StatusCode(500, new { error = "Internal Server Error", message = ex.StackTrace });
            }
        }
    }
}
