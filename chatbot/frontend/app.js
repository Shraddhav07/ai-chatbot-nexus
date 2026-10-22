/**
 * Nexus AI — Frontend Client Controller
 */
const BACKEND_BASE_URL = "http://127.0.0.1:8000";

const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const chatViewport = document.getElementById("chatViewport");
const backendStatus = document.getElementById("backendStatus");
const statusDot = document.getElementById("statusDot");
const modelPill = document.getElementById("modelPill");
const clearChatBtn = document.getElementById("clearChatBtn");
const personaSelect = document.getElementById("personaSelect");
const personaBadge = document.getElementById("personaBadge");
const avatarEmoji = document.getElementById("avatarEmoji");
const chips = document.querySelectorAll(".persona-chips-bar .chip");
const welcomeCard = document.getElementById("welcomeCard");
const welcomeDescription = document.getElementById("welcomeDescription");
const quickPrompts = document.getElementById("quickPrompts");

// Persona Metadata Configuration
const PERSONA_CONFIG = {
  teacher: {
    emoji: "🧑‍🏫",
    title: "Teacher Assistant",
    description: "Your personal <strong>Teacher Assistant</strong> is active. Ask any conceptual question, request step-by-step guides, or explore complex topics simplified.",
    prompts: [
      { label: "Explain Neural Networks", text: "Explain how neural networks learn in simple terms with an analogy" },
      { label: "Sync vs Async", text: "What is the difference between synchronous and asynchronous programming?" },
      { label: "Teach Recursion", text: "Teach me how recursion works with a real-world step-by-step example" }
    ]
  },
  summarizer: {
    emoji: "📄",
    title: "Text Summarizer",
    description: "The <strong>Text Summarizer</strong> is ready. Paste any lengthy text, meeting notes, or article to get a concise TL;DR, key takeaways, and action items.",
    prompts: [
      { label: "Summarize AI History", text: "Summarize the history of AI in 3 bullet points" },
      { label: "Executive Brief Format", text: "What makes an effective executive summary?" }
    ]
  },
  coach: {
    emoji: "💼",
    title: "Interview Coach",
    description: "The <strong>Interview Coach</strong> is active. Conduct mock interviews, ask for tough behavioral (STAR method) questions, or refine your answers.",
    prompts: [
      { label: "Mock Question: Python", text: "Ask me a challenging behavioral interview question for a Python Developer role" },
      { label: "STAR Technique", text: "Explain how to structure answers using the STAR method with an example" },
      { label: "System Design Prep", text: "How should I approach a 45-minute system design interview round?" }
    ]
  },
  travel: {
    emoji: "✈️",
    title: "Travel Guide",
    description: "The <strong>Travel Guide</strong> is ready. Ask for customized day-by-day itineraries, cultural etiquette, hidden culinary spots, or packing advice.",
    prompts: [
      { label: "3 Days in Kyoto", text: "Create a 3-day itinerary for Kyoto focusing on culture and food" },
      { label: "Solo Travel in Europe", text: "What are the top 5 tips for first-time solo travelers in Europe?" },
      { label: "Budgeting a Trip", text: "How should I plan a budget for a week in Southeast Asia?" }
    ]
  },
  assistant: {
    emoji: "🤖",
    title: "General Assistant",
    description: "Your <strong>General AI Assistant</strong> is ready to help with coding, writing, debugging, brainstorming, and daily problem solving.",
    prompts: [
      { label: "Code Optimization", text: "What are the best practices for writing clean and maintainable Python code?" },
      { label: "Brainstorm Ideas", text: "Brainstorm 5 innovative project ideas using LLMs and modern APIs" }
    ]
  }
};

let currentPersona = "teacher";

// Set Persona UI
function applyPersona(personaKey) {
  if (!PERSONA_CONFIG[personaKey]) return;
  currentPersona = personaKey;
  const config = PERSONA_CONFIG[personaKey];

  // Update Selector & Badge & Avatar
  if (personaSelect) personaSelect.value = personaKey;
  if (personaBadge) personaBadge.textContent = config.title;
  if (avatarEmoji) avatarEmoji.textContent = config.emoji;

  // Update Chips
  chips.forEach(chip => {
    if (chip.dataset.persona === personaKey) {
      chip.classList.add("active");
    } else {
      chip.classList.remove("active");
    }
  });

  // Update Welcome Card if still present
  if (welcomeDescription) welcomeDescription.innerHTML = config.description;
  if (quickPrompts) {
    quickPrompts.innerHTML = config.prompts.map(p => 
      `<button class="prompt-chip" data-prompt="${p.text}">${p.label}</button>`
    ).join("");
    attachQuickPromptEvents();
  }
}

// Attach Quick Prompt Clicks
function attachQuickPromptEvents() {
  document.querySelectorAll(".prompt-chip").forEach(btn => {
    btn.onclick = () => {
      const promptText = btn.getAttribute("data-prompt");
      if (promptText) {
        userInput.value = promptText;
        submitChat();
      }
    };
  });
}
attachQuickPromptEvents();

// Chip Click Listeners
chips.forEach(chip => {
  chip.addEventListener("click", () => {
    const p = chip.dataset.persona;
    applyPersona(p);
  });
});

// Dropdown Change Listener
if (personaSelect) {
  personaSelect.addEventListener("change", (e) => {
    applyPersona(e.target.value);
  });
}

// Health Check
async function checkBackendHealth() {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/health`);
    if (res.ok) {
      const data = await res.json();
      statusDot.className = "pulsing-status online";
      backendStatus.textContent = `Online • ${data.active_provider ? data.active_provider.toUpperCase() : 'Ready'}`;
      if (data.active_model) {
        modelPill.textContent = data.active_model;
      }
    } else {
      throw new Error("Offline");
    }
  } catch (err) {
    statusDot.className = "pulsing-status offline";
    backendStatus.textContent = "Engine Offline (Run 'python server.py')";
    modelPill.textContent = "Offline";
  }
}
checkBackendHealth();
setInterval(checkBackendHealth, 8000);

// Basic Markdown formatting for assistant text
function formatMarkdown(text) {
  if (!text) return "";
  let esc = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Bold **text**
  esc = esc.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  // Inline code `code`
  esc = esc.replace(/`([^`]+)`/g, "<code>$1</code>");
  // Bullets
  esc = esc.replace(/^\s*[-•]\s+(.*)$/gm, "<li>$1</li>");
  esc = esc.replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>");

  return esc;
}

// Append Message Row
function appendMessage(sender, text, isError = false) {
  // Remove welcome card on first message
  if (welcomeCard && welcomeCard.parentNode) {
    welcomeCard.remove();
  }

  const row = document.createElement("div");
  row.className = `message-row ${sender} ${isError ? 'error-row' : ''}`;

  const avatar = document.createElement("div");
  avatar.className = "msg-avatar";
  avatar.textContent = sender === "user" ? "👤" : (isError ? "⚠️" : PERSONA_CONFIG[currentPersona].emoji);

  const bubbleBody = document.createElement("div");
  bubbleBody.className = "bubble-body";

  const meta = document.createElement("div");
  meta.className = "bubble-meta";
  const nameLabel = sender === "user" ? "You" : (isError ? "System Alert" : PERSONA_CONFIG[currentPersona].title);
  const timeLabel = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  if (sender === "assistant" && !isError) {
    meta.innerHTML = `<span>${nameLabel} • ${timeLabel}</span><button class="copy-btn" title="Copy reply">Copy</button>`;
  } else {
    meta.innerHTML = `<span>${nameLabel} • ${timeLabel}</span>`;
  }

  const content = document.createElement("div");
  content.className = "formatted-content";
  if (sender === "assistant" && !isError) {
    content.innerHTML = formatMarkdown(text);
  } else {
    content.textContent = text;
  }

  bubbleBody.appendChild(meta);
  bubbleBody.appendChild(content);

  row.appendChild(avatar);
  row.appendChild(bubbleBody);

  chatViewport.appendChild(row);
  chatViewport.scrollTop = chatViewport.scrollHeight;

  // Copy button handler
  const copyBtn = bubbleBody.querySelector(".copy-btn");
  if (copyBtn) {
    copyBtn.onclick = () => {
      navigator.clipboard.writeText(text);
      copyBtn.textContent = "Copied!";
      setTimeout(() => copyBtn.textContent = "Copy", 2000);
    };
  }
}

// Show Typing Indicator
function showTypingIndicator() {
  const typingRow = document.createElement("div");
  typingRow.id = "typingIndicator";
  typingRow.className = "message-row assistant";
  typingRow.innerHTML = `
    <div class="msg-avatar">${PERSONA_CONFIG[currentPersona].emoji}</div>
    <div class="bubble-body">
      <div class="typing-dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
    </div>
  `;
  chatViewport.appendChild(typingRow);
  chatViewport.scrollTop = chatViewport.scrollHeight;
}

function removeTypingIndicator() {
  const ind = document.getElementById("typingIndicator");
  if (ind) ind.remove();
}

// Auto-expand textarea
userInput.addEventListener("input", function() {
  this.style.height = "auto";
  this.style.height = (this.scrollHeight) + "px";
});

// Keydown: Enter sends, Shift+Enter newlines
userInput.addEventListener("keydown", function(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    submitChat();
  }
});

// Clear Chat
clearChatBtn.addEventListener("click", () => {
  chatViewport.innerHTML = "";
  chatViewport.appendChild(welcomeCard);
  applyPersona(currentPersona);
});

// Submit Chat Logic
async function submitChat() {
  const rawText = userInput.value;
  const trimmed = rawText.trim();

  if (!trimmed) {
    userInput.value = "";
    return;
  }

  // Display User Message
  appendMessage("user", trimmed);
  userInput.value = "";
  userInput.style.height = "auto";
  userInput.focus();

  // Local Exit Command Check
  if (["exit", "quit", "q", "bye"].includes(trimmed.toLowerCase())) {
    appendMessage("assistant", "👋 Session closed. Refresh the page or select another persona to start a new chat.");
    return;
  }

  showTypingIndicator();

  try {
    const response = await fetch(`${BACKEND_BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: trimmed,
        persona: currentPersona
      })
    });

    removeTypingIndicator();

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      const detail = errData.detail || `Server Error (${response.status})`;
      appendMessage("assistant", detail, true);
      return;
    }

    const data = await response.json();
    if (data.success) {
      appendMessage("assistant", data.reply);
    } else {
      appendMessage("assistant", `[${data.error_type || 'Error'}]: ${data.error_message}`, true);
    }
  } catch (error) {
    removeTypingIndicator();
    appendMessage(
      "assistant",
      `Connection Error: Could not reach the backend at ${BACKEND_BASE_URL}. Ensure your server is running ('python server.py').`,
      true
    );
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  submitChat();
});
