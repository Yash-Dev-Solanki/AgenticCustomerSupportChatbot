using AgenticAPI.Infrastructure;
using MediatR;

namespace AgenticAPI.Application.UpdateChatSummary
{
    public class UpdateChatSummaryCommand : IRequestHandler<UpdateChatSummaryRequestModel, UpdateChatSummaryResponseModel>
    {
        private IChatService _chatService;

        public UpdateChatSummaryCommand(IChatService chatService)
        {
            _chatService = chatService;
        }

        public async Task<UpdateChatSummaryResponseModel> Handle(UpdateChatSummaryRequestModel request, CancellationToken cancellationToken)
        {
            var response = new UpdateChatSummaryResponseModel();
            try
            {
                var result = await _chatService.UpdateChatDetails(request.ChatId!, "Summary", request.Summary!);
                response.Success = true;
                response.StatusCode = System.Net.HttpStatusCode.Created;
                response.Chat = result;
            }
            catch (ArgumentException ex)
            {
                response.Success = false;
                response.StatusCode = System.Net.HttpStatusCode.BadRequest;
                response.Errors!.Add(ex.Message);
            }
            catch (Exception ex)
            {
                response.Success = false;
                response.StatusCode = System.Net.HttpStatusCode.InternalServerError;
                response.Errors!.Add(ex.Message);
            }

            return response;
        }
    }
}
