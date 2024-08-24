document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.getElementById('toggle-chatbot');
    const chatbotContainer = document.getElementById('chatbot-container');
    const closeButton = document.getElementById('close-chatbot');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    toggleButton.addEventListener('click', () => {
        chatbotContainer.classList.toggle('visible');
    });

    closeButton.addEventListener('click', () => {
        chatbotContainer.classList.remove('visible');
    });

    function addMessage(message, isUser = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
        
        // Split the message into paragraphs and add them with line breaks
        const paragraphs = message.split('\n\n');
        paragraphs.forEach((paragraph, index) => {
            const p = document.createElement('p');
            p.textContent = paragraph;
            messageElement.appendChild(p);
            
            // Add a line break between paragraphs, except for the last one
            if (index < paragraphs.length - 1) {
                messageElement.appendChild(document.createElement('br'));
            }
        });

        chatbotMessages.appendChild(messageElement);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function addLoadingIndicator() {
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('loading');
        loadingElement.innerHTML = '<span></span><span></span><span></span>';
        chatbotMessages.appendChild(loadingElement);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        return loadingElement;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);
            userInput.value = '';

            const loadingIndicator = addLoadingIndicator();

            try {
                const response = await fetch('/api/chatbot/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message }),
                });

                loadingIndicator.remove();

                if (response.ok) {
                    const data = await response.json();
                    addMessage(data.response);
                } else {
                    addMessage('Error: Unable to get a response from the chatbot.');
                }
            } catch (error) {
                console.error('Error:', error);
                loadingIndicator.remove();
                addMessage('Error: Unable to connect to the chatbot service.');
            }
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});