namespace AgenticAPI.Domain
{
    public class ChatMessage
    {
        public string? Role { get; set; }
        public string? Message { get; set; }
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }
}
