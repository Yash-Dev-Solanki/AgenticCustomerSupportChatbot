class Endpoints:
    GET_CUSTOMER_BY_ID = "http://localhost:5142/api/Customer"

    CHECK_CUSTOMER_ID = "http://localhost:5142/api/Customer/CheckCustomer"

    VERIFY_CUSTOMER_ID = "http://localhost:5142/api/Customer/VerifyCustomer"

    UPDATE_CUSTOMER_EMAIL = "http://localhost:5142/api/Customer/UpdateEmail"

    UPDATE_CUSTOMER_PAYMENT_REMINDER = "http://localhost:5142/api/Customer/UpdatePaymentReminder"

    GET_CHAT_BY_CUSTOMER_ID = "http://localhost:5142/api/Chat/GetChatsForCustomer"

    CREATE_NEW_CHAT = "http://localhost:5142/api/Chat/CreateChat"

    ADD_MESSAGES_TO_CHAT = "http://localhost:5142/api/Chat/AddMessages"

    GET_MESSAGES_BY_CHAT_ID = "http://localhost:5142/api/Chat/{chatId}"

    SET_CHAT_SUMMARY = "http://localhost:5142/api/Chat/SetChatSummary"

    FETCH_LOAN_STATEMENT = "http://localhost:5142/api/LoanStatement"
