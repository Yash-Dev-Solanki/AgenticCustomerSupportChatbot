using System;
using System.Net;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using MediatR;
using AgenticAPI.Infrastructure;
using Microsoft.AspNetCore.Http.HttpResults;
using AgenticAPI.Application.GetLoanStatement;
using AgenticAPI.Domain;
using System.ComponentModel.DataAnnotations;
using MongoDB.Bson;
using AgenticAPI.Application.AddLoanDetails;
using AgenticAPI.Application.AddLoanPayment;

namespace AgenticAPI.WebAPI.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class LoanStatementController : ControllerBase
    {
        private readonly IMediator _mediator;

        public LoanStatementController(IMediator mediator)
        {
            _mediator = mediator;
        }

        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [ActionName("GetLoanStatement")]
        public async Task<IActionResult> Get([FromHeader] string customerId)
        {
            try
            {
                if (string.IsNullOrEmpty(customerId))
                {
                    return BadRequest(new
                    {
                        Success = false,
                        Errors = new[] { "CustomerId header is required" }
                    });
                }

                var request = new GetLoanStatementRawRequestModel(customerId);
                var response = await _mediator.Send(request);
                if (response.StatusCode == HttpStatusCode.OK)
                {
                    return Ok(response);
                }
                else if (response.StatusCode == HttpStatusCode.BadRequest)
                {
                    return BadRequest(response);
                }
                else if (response.StatusCode == HttpStatusCode.NotFound)
                {
                    return NotFound(response);
                }
                else
                {
                    return StatusCode(500, new
                    {
                        Success = false,
                        Errors = new[] { "Internal Server Error" }
                    });
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, new
                {
                    Success = false,
                    Errors = new[] { "Internal Server Error", ex.Message }
                });
            }
        }
        [HttpPost("AddLoanDetails")]
        public async Task<IActionResult> AddLoanDetails([FromBody] AddLoanDetailsRawRequestModel request)
        {
            var response = await _mediator.Send(request);
            if (response.Success)
                return Created("", response);
            else
                return BadRequest(response);
        }

        [HttpPost("AddLoanPayment")]
        public async Task<IActionResult> AddLoanPayment([FromBody] AddLoanPaymentRawRequestModel request)
        {
            var response = await _mediator.Send(request);
            if (response.Success)
                return Created("", response);
            else
                return BadRequest(response);
        }
    }
}
