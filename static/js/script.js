async function postData(url = "", data = {}) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return response.json();
}

function appendChatMessage(role, text) {
  const container = document.getElementById("chat-container");
  const bubble = document.createElement("div");

  bubble.className = `p-3 my-2 rounded-md max-w-[70%] whitespace-pre-line ${
    role === "user" ? "bg-blue-600 self-end ml-auto" : "bg-gray-700 self-start"
  }`;

  bubble.textContent = text;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

document.addEventListener("DOMContentLoaded", () => {
  const sendButton = document.getElementById("sendButton");
  const inputField = document.getElementById("questionInput");
  const chatContainer = document.getElementById("chat-container");

  sendButton.addEventListener("click", async (e) => {
    e.preventDefault();
    const questionText = inputField.value.trim();
    if (!questionText) return;

    inputField.value = "";
    appendChatMessage("user", questionText);

    const result = await postData("/api", { question: questionText });
    appendChatMessage("bot", result.answer || "No answer.");
  });

  const historyItems = document.querySelectorAll(".chat-history-item");
  historyItems.forEach((item) => {
    item.addEventListener("click", () => {
      const question = item.dataset.question;
      const answer = item.dataset.answer;
      chatContainer.innerHTML = "";
      appendChatMessage("user", question);
      appendChatMessage("bot", answer);
    });
  });

  const resetBtn = document.getElementById("resetForm");
  if (resetBtn) {
    resetBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      await fetch("/reset", { method: "POST" });
      window.location.reload();
    });
  }
});
