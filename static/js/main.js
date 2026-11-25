/**
 * main.js - Core UI helpers, animations, and interactivity
 */

// ── Number Counter Animation ─────────────────────────────────────────────────
function animateCounter(el, target) {
  if (!el || target === undefined || isNaN(target)) return;
  const duration = 1000;
  const startTime = performance.now();
  const isFloat = target % 1 !== 0;

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const currentVal = target * ease;
    el.textContent = isFloat ? currentVal.toFixed(1) : Math.round(currentVal);

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      el.textContent = target;
    }
  }

  requestAnimationFrame(update);
}

// ── Score Ring Animation ─────────────────────────────────────────────────────
function animateScoreRing(score) {
  const ring = document.getElementById('ringFill');
  if (!ring) return;
  const circumference = 414.7;
  const offset = circumference - (circumference * (score / 100));
  setTimeout(() => {
    ring.style.transition = 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)';
    ring.style.strokeDashoffset = offset;
  }, 150);
}

// ── Quick Add Skill Chip ─────────────────────────────────────────────────────
function addSkill(skill) {
  const input = document.querySelector('input[name="skills"]');
  if (!input) return;
  const existing = input.value
    .split(',')
    .map(s => s.trim())
    .filter(Boolean);
  if (!existing.includes(skill)) {
    existing.push(skill);
    input.value = existing.join(', ');
    input.focus();
  }
}

// ── Password Visibility Toggle ───────────────────────────────────────────────
function togglePwd(id) {
  const inp = document.getElementById(id);
  const icon = document.getElementById('eyeIcon-' + id);
  if (!inp) return;
  if (inp.type === 'password') {
    inp.type = 'text';
    if (icon) icon.className = 'bi bi-eye-slash-fill';
  } else {
    inp.type = 'password';
    if (icon) icon.className = 'bi bi-eye-fill';
  }
}

// ── Global Event Handlers & Theme Management ─────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Theme (Dark / Light Mode)
  const savedTheme = localStorage.getItem('placeready_theme') || 'light';
  applyTheme(savedTheme);

  const darkToggle = document.getElementById('darkToggle');
  if (darkToggle) {
    darkToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const nextTheme = current === 'dark' ? 'light' : 'dark';
      applyTheme(nextTheme);
    });
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('placeready_theme', theme);
    const darkIcon = document.getElementById('darkIcon');
    if (darkIcon) {
      darkIcon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
      darkIcon.style.color = theme === 'dark' ? '#f59e0b' : '';
    }
  }

  // Sidebar Mobile Toggle
  const sidebar = document.getElementById('sidebar');
  const sidebarOverlay = document.getElementById('sidebarOverlay');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebarClose = document.getElementById('sidebarClose');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('open');
      if (sidebarOverlay) sidebarOverlay.classList.toggle('active');
    });
  }

  if (sidebarClose && sidebar) {
    sidebarClose.addEventListener('click', () => {
      sidebar.classList.remove('open');
      if (sidebarOverlay) sidebarOverlay.classList.remove('active');
    });
  }

  if (sidebarOverlay && sidebar) {
    sidebarOverlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      sidebarOverlay.classList.remove('active');
    });
  }

  // Auto-dismiss Flash Alerts
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(f => {
    setTimeout(() => {
      f.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      f.style.opacity = '0';
      f.style.transform = 'translateY(-10px)';
      setTimeout(() => f.remove(), 400);
    }, 4500);
  });
});
