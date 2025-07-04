using AgenticAPI.Domain;

namespace AgenticAPI.Application.UpdateChatSummary
{
    public class UpdateChatSummaryResponseModel: BaseResponseModel
    {
        public Chat? Chat { get; set; }

        public UpdateChatSummaryResponseModel(): base()
        {

        }
    }
}
