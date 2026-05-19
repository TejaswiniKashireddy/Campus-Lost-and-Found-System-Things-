/* ── Auto-dismiss flash messages after 4 s ── */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.flash').forEach((el, i) => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s, transform .4s';
      el.style.opacity    = '0';
      el.style.transform  = 'translateX(110%)';
      setTimeout(() => el.remove(), 400);
    }, 4000 + i * 400);
  });
});

/* ── Image preview in upload zone ── */
function previewImg(input) {
  const content = document.getElementById('upContent');
  const preview = document.getElementById('imgPreview');
  const img     = document.getElementById('prevImg');
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = e => {
      img.src              = e.target.result;
      content.style.display = 'none';
      preview.style.display = 'block';
    };
    reader.readAsDataURL(input.files[0]);
  }
}

/* ── Drag-and-drop on upload zone ── */
const zone = document.getElementById('uploadZone');
if (zone) {
  zone.addEventListener('dragover', e => {
    e.preventDefault();
    zone.style.borderColor = 'var(--primary)';
    zone.style.background  = 'var(--primary-lt)';
  });
  zone.addEventListener('dragleave', () => {
    zone.style.borderColor = '';
    zone.style.background  = '';
  });
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.style.borderColor = '';
    zone.style.background  = '';
    const file  = e.dataTransfer.files[0];
    const input = document.getElementById('imgInput');
    if (file && input) {
      const dt = new DataTransfer();
      dt.items.add(file);
      input.files = dt.files;
      previewImg(input);
    }
  });
}

/* ── Admin tab switching ── */
function switchTab(name, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  const panel = document.getElementById('tab-' + name);
  if (panel) panel.classList.add('active');
  if (btn)   btn.classList.add('active');
}
