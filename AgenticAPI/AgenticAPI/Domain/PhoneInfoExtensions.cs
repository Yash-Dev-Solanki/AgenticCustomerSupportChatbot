namespace AgenticAPI.Domain
{
    public static class PhoneInfoExtensions
    {
        public static string GetExtractedHomePhone(this PhoneInfo phoneInfo)
        {
            if (string.IsNullOrEmpty(phoneInfo.homePhone))
                return "";

            return phoneInfo.homePhone.Length <= 4
                ? phoneInfo.homePhone
                : phoneInfo.homePhone.Substring(phoneInfo.homePhone.Length - 4);
        }

        public static string? GetExtractedWorkPhone(this PhoneInfo phoneInfo)
        {
            if (string.IsNullOrEmpty(phoneInfo.workPhone))
                return null;

            return phoneInfo.workPhone.Length <= 4
                ? phoneInfo.workPhone
                : phoneInfo.workPhone.Substring(phoneInfo.workPhone.Length - 4);
        }
    }
}
