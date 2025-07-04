using AgenticAPI.Infrastructure;
using MediatR;

namespace AgenticAPI.Application.GetChatById
{
    public class GetChatByIdCommand: IRequestHandler<GetChatByIdRequestModel, GetChatByIdResponseModel>
    {
        private readonly IChatService _chatService;
        public GetChatByIdCommand(IChatService chatService) 
        { 
            _chatService = chatService;
        }

        public async Task<GetChatByIdResponseModel> Handle(GetChatByIdRequestModel request, CancellationToken cancellationToken)
        {
            var response = new GetChatByIdResponseModel();
            try
            {
                var result = await _chatService.GetByChatId(request.ChatId!);

                if (result == null)
                {
                    response.Success = true;
                    response.StatusCode = System.Net.HttpStatusCode.BadRequest;
                    response.Errors!.Add("Chat Id not found in Mongo");
                }
                else
                {
                    response.chat = result;
                    response.Success = true;
                    response.StatusCode = System.Net.HttpStatusCode.OK;
                }
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
