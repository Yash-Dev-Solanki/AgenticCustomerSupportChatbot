using AgenticAPI.Domain;
using AgenticAPI.Infrastructure;
using MediatR;
using MongoDB.Bson.Serialization;
using System;
using System.Net;
using System.Threading;
using System.Threading.Tasks;
using AutoMapper;

namespace AgenticAPI.Application.GetLoanStatement
{
    public class GetLoanStatementCommand : IRequestHandler<GetLoanStatementRawRequestModel, GetLoanStatementResponseModel>
    {
        private readonly ILoanService _loanService;
        private readonly IMapper _mapper;

        public GetLoanStatementCommand(ILoanService loanService,IMapper mapper)
        {
            _loanService = loanService;
            _mapper = mapper;
        }

        public async Task<GetLoanStatementResponseModel> Handle(GetLoanStatementRawRequestModel request, CancellationToken cancellationToken)
        {
            var response = new GetLoanStatementResponseModel();

            try
            {
                if (string.IsNullOrEmpty(request.CustomerId))
                {
                    response.Success = false;
                    response.StatusCode = HttpStatusCode.BadRequest;
                    response.Errors!.Add("CustomerId cannot be null or empty");
                    return response;
                }

                var loanDetails = await _loanService.GetLoanDetailsByCustomerId(request.CustomerId);
                if (loanDetails == null)
                {
                    response.Success = false;
                    response.StatusCode = HttpStatusCode.NotFound;
                    response.Errors!.Add("Loan details not found for the provided customer Id");
                    return response;
                }

                var payments = await _loanService.GetPaymentsByLoanAccount(loanDetails.LoanAccountNumber);

                // Map domain models to application models
                response.CustomerId = loanDetails.CustomerId;
                response.LoanAccountNumber = loanDetails.LoanAccountNumber;
                response.LoanSummary = _mapper.Map<LoanSummary>(loanDetails);
                response.PaymentHistory = _mapper.Map<List<LoanPayment>>(payments);

                response.StatusCode = HttpStatusCode.OK;
            }
            catch (Exception ex)
            {
                response.Success = false;
                response.StatusCode = HttpStatusCode.InternalServerError;
                response.Errors!.Add(ex.Message);
            }

            return response;
        }

    }
}
