class Endpoints:
    GET_CUSTOMER_BY_ID = "https://localhost:7260/api/Customer"

    CHECK_CUSTOMER = "https://localhost:7260/api/Customer/CheckCustomer"

    VERIFY_CUSTOMER_ID = "https://localhost:7260/api/Customer/VerifyCustomer"
    
    UPDATE_CUSTOMER_EMAIL = "https://localhost:7260/api/Customer/UpdateEmail"

    UPDATE_CUSTOMER_PAYMENT_REMINDER = "https://localhost:7260/api/Customer/UpdatePaymentReminder"

    GET_CHAT_BY_CUSTOMER_ID = "https://localhost:7260/api/Chat/GetChatsForCustomer"

    CREATE_NEW_CHAT = "https://localhost:7260/api/Chat/CreateChat"

    ADD_MESSAGES_TO_CHAT = "https://localhost:7260/api/Chat/AddMesssages"

    GET_MESSAGES_BY_CHAT_ID = "https://localhost:7260/api/Chat/{chatId}"

    SET_CHAT_SUMMARY = "https://localhost:7260/api/Chat/SetChatSummary"

    FETCH_LOAN_STATEMENT = "https://localhost:7260/api/LoanStatement"