const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Helper function to display messages
function displayMessage(elementId, message, type) {
    const messageDiv = document.getElementById(elementId);
    messageDiv.textContent = message;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
}

// Function to make API calls
async function callApi(endpoint, data) {
    try {
        const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (!response.ok) {
            const errorMessage = result.error || result.detail || JSON.stringify(result);
            throw new Error(errorMessage);
        }
        return result;
    } catch (error) {
        console.error(`API Call to ${endpoint} failed:`, error);
        throw error; // Re-throw to be caught by specific form handlers
    }
}

// 1. Register User
document.getElementById('registerForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const email = document.getElementById('registerEmail').value;
    const messageDivId = 'registerMessage';
    displayMessage(messageDivId, '', ''); // Clear previous message

    try {
        const result = await callApi('register', { email });
        displayMessage(messageDivId, result.message, 'success');
    } catch (error) {
        displayMessage(messageDivId, `Error: ${error.message}`, 'error');
    }
});

// 2. Request OTP
document.getElementById('requestOtpForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const email = document.getElementById('requestEmail').value;
    const messageDivId = 'requestOtpMessage';
    displayMessage(messageDivId, '', ''); // Clear previous message

    try {
        const result = await callApi('request-otp', { email });
        displayMessage(messageDivId, result.message + " (Check your PyCharm terminal for OTP)", 'success');
    } catch (error) {
        displayMessage(messageDivId, `Error: ${error.message}`, 'error');
    }
});

// 3. Verify OTP
document.getElementById('verifyOtpForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const email = document.getElementById('verifyEmail').value;
    const otp = document.getElementById('verifyOtp').value;
    const messageDivId = 'verifyOtpMessage';
    const tokenResultDiv = document.getElementById('tokenResult');
    const jwtTokenParagraph = document.getElementById('jwtToken');

    displayMessage(messageDivId, '', ''); // Clear previous message
    tokenResultDiv.style.display = 'none'; // Hide token result initially

    try {
        const result = await callApi('verify-otp', { email, otp });
        displayMessage(messageDivId, result.message, 'success');

        if (result.token) {
            jwtTokenParagraph.textContent = result.token;
            tokenResultDiv.style.display = 'block';
        }
    } catch (error) {
        displayMessage(messageDivId, `Error: ${error.message}`, 'error');
        tokenResultDiv.style.display = 'none';
    }
});