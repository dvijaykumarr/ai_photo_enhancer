// static/script.js
async function handleTextMessage(message) {
    addMessage(message, 'user');
    showTypingIndicator();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        hideTypingIndicator();
        
        if (data.status === 'success') {
            addMessage(data.response, 'bot');
        } else {
            addMessage('Apologies, I encountered an issue. Please try again.', 'bot');
        }
    } catch (error) {
        hideTypingIndicator();
        console.error('Error:', error);
        addMessage('Error communicating with the server. Please try again.', 'bot');
    }
}

async function handleImageUpload(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        addImageMessage(e.target.result, 'user');
    };
    reader.readAsDataURL(file);
    
    showTypingIndicator();
    const processingMessage = addMessage('Enhancing your image...', 'bot');
    
    try {
        const response = await fetch('/enhance', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        hideTypingIndicator();
        
        if (data.status === 'success') {
            processingMessage.remove();
            addImageMessage(data.enhanced_url, 'bot');
            addMessage('Here\'s your enhanced image! Let me know if you need anything else.', 'bot');
        } else {
            addMessage('Failed to enhance image. Please try again with a different file.', 'bot');
        }
    } catch (error) {
        hideTypingIndicator();
        processingMessage.remove();
        console.error('Error:', error);
        addMessage('Image processing error: ' + error.message, 'bot');
    }
}