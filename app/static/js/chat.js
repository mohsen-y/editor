/**
 * Chat Scripts
 */

const chatSocketUrl = `ws://${window.location.host}/ws/files/${filePk}/chat/`;
const chatSocket = new WebSocket(chatSocketUrl);

const chatMessages = document.getElementById("chat-messages");
const messageInput = document.getElementById("message-input");
const messageSubmit = document.getElementById("message-submit");

messageInput.focus();

messageInput.onkeyup = function(e) {
    if (e.keyCode === 13) messageSubmit.click();
};

document.querySelector("#message-submit").onclick = function(e) {
    const message_content = messageInput.value;
    if (message_content) {
        chatSocket.send(JSON.stringify({"message_content": message_content}));
        messageInput.value = "";
    }
    messageInput.focus();
};

chatSocket.onopen = function(e) {
    chatMessages.scrollTop = chatMessages.scrollHeight;
};

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    const messageCreator = (authenticatedUserUsername == data.message.creator.username) ? "You" : data.message.creator.username;
    const messageCreatedAt = new Date(data.message.created_at);
    const messageCreatedAtFormatted = Intl.DateTimeFormat("en-Us", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
    }).format(messageCreatedAt);

    const chatMessage = `
        <div class="chat-message">
          <span class="creator">${messageCreator}</span>
          <span class="datetime">${messageCreatedAtFormatted}</span>
          <p>${data.message.content}</p>
        </div>
    `;

    chatMessages.innerHTML += chatMessage;
    chatMessages.scrollTop = chatMessages.scrollHeight;
};

chatSocket.onclose = function(e) {};

chatSocket.onerror = function(e) {};
