/* ═══════════════════════════════════════════════
   CampusDate — Main JavaScript
   Handles: likes (AJAX), chat polling, alerts,
            mobile nav, match popup, UI helpers
═══════════════════════════════════════════════ */

// ── CSRF Token Helper ───────────────────────────
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
         document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))
                       ?.split('=')[1] || '';
}

// ── Auto-dismiss Alerts ─────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    // Click to dismiss
    alert.addEventListener('click', () => alert.remove());
    // Auto-dismiss after 4 seconds
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateX(120%)';
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });
});

// ── Mobile Navigation Toggle ────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.navbar-toggle');
  const nav = document.querySelector('.navbar-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
    // Close nav when clicking a link
    nav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => nav.classList.remove('open'));
    });
  }
});

// ── Like Button (AJAX) ──────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.like-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('.btn-like');
      const userId = form.dataset.userId;

      btn.disabled = true;

      try {
        const res = await fetch(form.action, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
          },
        });
        const data = await res.json();

        if (data.liked) {
          btn.classList.add('liked');
          btn.innerHTML = '❤️ Liked';
        } else {
          btn.classList.remove('liked');
          btn.innerHTML = '🤍 Like';
        }

        // Show match popup if it's a new match!
        if (data.is_match && data.match_message) {
          showMatchPopup(data.match_message);
        }
      } catch (err) {
        console.error('Like failed:', err);
      } finally {
        btn.disabled = false;
      }
    });
  });
});

// ── Match Popup ─────────────────────────────────
function showMatchPopup(message) {
  const overlay = document.createElement('div');
  overlay.className = 'match-popup-overlay';
  overlay.innerHTML = `
    <div class="match-popup">
      <div class="match-popup-hearts">💕</div>
      <h2>It's a Match!</h2>
      <p>${message}</p>
      <a href="/matches/" class="btn btn-primary">See Your Matches</a>
      <button onclick="this.closest('.match-popup-overlay').remove()"
              class="btn btn-ghost mt-2" style="margin-left:8px">Keep Browsing</button>
    </div>
  `;
  document.body.appendChild(overlay);
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.remove();
  });
}

// ── Chat: Auto-scroll & Polling ─────────────────
(function initChat() {
  const chatMessages = document.getElementById('chatMessages');
  const matchId = document.body.dataset.matchId;

  if (!chatMessages || !matchId) return;

  // Scroll to bottom on load
  chatMessages.scrollTop = chatMessages.scrollHeight;

  let lastMsgId = getLastMessageId();

  // Poll for new messages every 3 seconds
  setInterval(async () => {
    try {
      const res = await fetch(`/chat/${matchId}/messages/?after=${lastMsgId}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      const data = await res.json();
      if (data.messages && data.messages.length > 0) {
        data.messages.forEach(msg => appendMessage(msg));
        lastMsgId = data.messages[data.messages.length - 1].id;
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
    } catch (err) {
      // Silent fail — user still sees existing messages
    }
  }, 3000);

  function getLastMessageId() {
    const bubbles = chatMessages.querySelectorAll('[data-msg-id]');
    if (bubbles.length === 0) return 0;
    return parseInt(bubbles[bubbles.length - 1].dataset.msgId) || 0;
  }

  function appendMessage(msg) {
    const wrap = document.createElement('div');
    wrap.className = `message-bubble-wrap ${msg.is_mine ? 'mine' : ''}`;
    wrap.dataset.msgId = msg.id;
    wrap.innerHTML = `
      <div class="message-bubble ${msg.is_mine ? 'mine' : 'theirs'}">
        ${escapeHtml(msg.content)}
      </div>
      <div class="message-time">${msg.time}</div>
    `;
    chatMessages.appendChild(wrap);
  }

  // Submit message via AJAX
  const chatForm = document.getElementById('chatForm');
  const msgInput = document.getElementById('messageInput');
  if (chatForm) {
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const content = msgInput.value.trim();
      if (!content) return;

      const submitBtn = chatForm.querySelector('button[type=submit]');
      submitBtn.disabled = true;

      try {
        const res = await fetch(chatForm.action, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({ content }),
        });

        if (res.ok) {
          msgInput.value = '';
          msgInput.style.height = 'auto';
          // Immediately show the sent message
          appendMessage({
            id: Date.now(), // temp id
            content,
            is_mine: true,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          });
          chatMessages.scrollTop = chatMessages.scrollHeight;
        }
      } catch (err) {
        console.error('Send failed:', err);
      } finally {
        submitBtn.disabled = false;
        msgInput.focus();
      }
    });

    // Auto-resize textarea
    msgInput.addEventListener('input', () => {
      msgInput.style.height = 'auto';
      msgInput.style.height = Math.min(msgInput.scrollHeight, 120) + 'px';
    });

    // Ctrl/Cmd+Enter to send
    msgInput.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        chatForm.dispatchEvent(new Event('submit'));
      }
    });
  }
})();

// ── Profile Picture Preview ─────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const picInput = document.querySelector('input[name="profile_picture"]');
  const preview = document.getElementById('picPreview');
  if (picInput && preview) {
    picInput.addEventListener('change', () => {
      const file = picInput.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          preview.src = e.target.result;
          preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
      }
    });
  }
});

// ── Utility: XSS-safe HTML escape ───────────────
function escapeHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

// ── Character Counter for Bio ───────────────────
document.addEventListener('DOMContentLoaded', () => {
  const bio = document.querySelector('textarea[name="bio"]');
  if (bio) {
    const counter = document.createElement('div');
    counter.className = 'form-hint';
    bio.parentNode.appendChild(counter);
    const update = () => {
      const left = 500 - bio.value.length;
      counter.textContent = `${left} characters remaining`;
      counter.style.color = left < 50 ? 'var(--rose)' : '';
    };
    bio.addEventListener('input', update);
    update();
  }
});
