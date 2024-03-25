
const key='e44f77643020ff731b4f';
const cluster = "mt1"


// Initialize Pusher
const pusher = new Pusher(key, {
    cluster: cluster,
    encrypted: true
});

// Subscribe to the chat channel
const channelName = getChatChannelName(USER_ID, RECIPIENT_ID);
const channel = pusher.subscribe(channelName);

// Bind to a 'new-message' event within the chat channel
channel.bind('new-message', function(data) {
    // Append new messages to the chat
    // $('#chat-box').append(`<p>${data.message}</p>`);
    const messageDiv = `<div class="${data.sender === USER_ID ? 'me' : 'reply'}">
    ${data.sender}: ${data.message}
    </div>`;
    $('#chat-box').append(messageDiv);
});

// Form submission to send a new message
$('#message-form').submit(function(e) {
    e.preventDefault();
    const message = $('#message-input').val();

    // AJAX POST request to send the message
    $.ajax({
        type: 'POST',
        url: '/send_message/',  // The endpoint in Django app urls.py
        data: {
            'receiver_id': RECIPIENT_ID,
            'message': message,
            'csrfmiddlewaretoken': getCSRFToken()  // Handle CSRF token
        },
        success: function(response) {
            console.log('Message sent successfully!');
            $('#message-input').val('');  // Clear the input field
            // append the message to the chat window
            $('#chat-box').append(`<p>${message}</p>`);
        },
        error: function() {
            alert('There was an error sending your message.');
        }
    });
});

// Utility function to generate the channel name consistently
function getChatChannelName(userId1, userId2) {
    return `private-chat-${Math.min(userId1, userId2)}-${Math.max(userId1, userId2)}`;
}

// Utility function to get the CSRF token
function getCSRFToken() {
    return document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
}