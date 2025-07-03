using MediatR;

namespace AgenticAPI.Application.UpdateChatSummary
{
    public class UpdateChatSummaryRequestModel: IRequest<UpdateChatSummaryResponseModel>
    {
        public string? ChatId { get; set; }
        public string? Summary { get; set; }
    }
}
