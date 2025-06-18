using System.Net;

namespace AgenticAPI.Domain
{
    public class BaseResponseModel
    {
        public HttpStatusCode StatusCode { get; set; }
        public bool Success { get; set; }
        public List<string>? Errors { get; set; }

        public BaseResponseModel() 
        {
            Success = true;
            Errors = new List<string>();
        }
    }
}
