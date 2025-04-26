const API_URL = 'http://127.0.0.1:5000'; // Replace with your API URL

const messagesContainer = document.getElementById('messages');
const inputField = document.getElementById('inputField');
const sendButton = document.getElementById('sendButton');

function fetchConversationHistory() {
    fetch(`${API_URL}/history`)
        .then(response => response.json())
        .then(data => {
            console.log('API Response:', data); // Log the full response for debugging

            if (data.message) {
                displayMessage('system', data.message);
            } else {
                const conversationHistory = data.conversation_history;
                if (Array.isArray(conversationHistory)) {
                    conversationHistory.forEach(message => {
                        displayMessage(message.role, message.content);
                    });
                } else {
                    console.error('Invalid conversation history format:', conversationHistory);
                }
            }
        })
        .catch(error => console.error('Error fetching conversation history:', error));
}

function displayMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.textContent = `${role}: ${content}`;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight; // Scroll to the bottom
}

function sendMessage() {
    const userMessage = inputField.value.trim();
    if (userMessage) {
        displayMessage('You', userMessage);
        inputField.value = ''; // Clear input field

        // Send message to API
        fetch(`${API_URL}/chat/?&message=${encodeURIComponent(userMessage)}`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            const assistantResponse = data.response;
            displayMessage('Assistant', assistantResponse);
        })
        .catch(error => console.error('Error sending message:', error));
    }
}

// Send message when clicking the send button
sendButton.addEventListener('click', sendMessage);

// Send message when "Enter" is pressed
inputField.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});