(function () {
  "use strict";

  function bootstrapChatbot() {
    var root = document.getElementById("shafinChatbot");
    if (!root) {
      return;
    }

    var fab = document.getElementById("shafinChatFab");
    var panel = document.getElementById("shafinChatPanel");
    var closeButton = document.getElementById("shafinChatClose");
    var messagesEl = document.getElementById("shafinChatMessages");
    var typingEl = document.getElementById("shafinChatTyping");
    var form = document.getElementById("shafinChatForm");
    var input = document.getElementById("shafinChatInput");
    var sendButton = document.getElementById("shafinChatSend");

    if (!fab || !panel || !closeButton || !messagesEl || !typingEl || !form || !input || !sendButton) {
      return;
    }

    var history = [];

    function toggle(openState) {
      if (openState) {
        root.classList.add("is-open");
        window.setTimeout(function () {
          input.focus();
        }, 120);
      } else {
        root.classList.remove("is-open");
      }
    }

    function escapeHtml(value) {
      return (value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function renderMarkdown(text) {
      if (window.marked && window.DOMPurify) {
        marked.setOptions({
          breaks: true,
          gfm: true
        });
        var rawHtml = marked.parse(text || "");
        return DOMPurify.sanitize(rawHtml);
      }

      return escapeHtml(text).replace(/\n/g, "<br>");
    }

    function appendMessage(role, text) {
      var bubble = document.createElement("article");
      bubble.className = "shafin-chatbot-message " + (role === "user" ? "is-user" : "is-assistant");
      if (role === "assistant") {
        bubble.innerHTML = renderMarkdown(text);
        var shouldExpand = (text || "").length > 260 || /\n\s*[-*0-9]/.test(text || "") || /```/.test(text || "");
        root.classList.toggle("is-wide", shouldExpand);
      } else {
        bubble.textContent = text;
      }
      messagesEl.appendChild(bubble);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function setLoading(isLoading) {
      typingEl.hidden = !isLoading;
      input.disabled = isLoading;
      sendButton.disabled = isLoading;
      if (isLoading) {
        messagesEl.scrollTop = messagesEl.scrollHeight;
      }
    }

    function readAssistantText(data) {
      if (!data || typeof data.reply !== "string") {
        return "I could not generate a response right now. Please try again.";
      }
      return data.reply.trim() || "I could not generate a response right now. Please try again.";
    }

    async function askAssistant(messageText) {
      var payload = {
        message: messageText,
        page: window.location.pathname,
        pageTitle: document.title || "",
        history: history
      };

      var response = await fetch("/api/chatbot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        credentials: "same-origin",
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        var fallbackText = "The assistant is temporarily unavailable. Please try again in a moment.";
        try {
          var errData = await response.json();
          if (errData && typeof errData.error === "string") {
            fallbackText = errData.error;
          }
        } catch (err) {
          // Ignore JSON parse errors and keep fallback text.
        }
        throw new Error(fallbackText);
      }

      return response.json();
    }

    fab.addEventListener("click", function () {
      toggle(true);
    });

    closeButton.addEventListener("click", function () {
      toggle(false);
    });

    form.addEventListener("submit", async function (event) {
      event.preventDefault();

      var text = (input.value || "").trim();
      if (!text) {
        return;
      }

      appendMessage("user", text);
      history.push({ role: "user", content: text });
      input.value = "";
      setLoading(true);

      try {
        var data = await askAssistant(text);
        var answer = readAssistantText(data);
        appendMessage("assistant", answer);
        history.push({ role: "assistant", content: answer });
      } catch (error) {
        var message = error && error.message ? error.message : "Something went wrong while contacting the assistant.";
        appendMessage("assistant", message);
        history.push({ role: "assistant", content: message });
      } finally {
        setLoading(false);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootstrapChatbot);
  } else {
    bootstrapChatbot();
  }
})();
