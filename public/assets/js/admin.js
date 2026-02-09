/**
 * Scripts d'administration — Fête du Cidre
 * Vanilla JS uniquement.
 */
(function () {
    'use strict';

    /* ── Confirmation de suppression ── */
    document.querySelectorAll('.confirm-delete').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
                e.preventDefault();
            }
        });
    });

    /* ── Auto-dismiss des messages flash après 5 s ── */
    document.querySelectorAll('.flash').forEach(function (el) {
        setTimeout(function () {
            el.style.transition = 'opacity 0.3s ease';
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 300);
        }, 5000);
    });

    /* ── Génération automatique de slug ── */
    var titleInput = document.getElementById('title');
    var slugInput = document.getElementById('slug');

    if (titleInput && slugInput && !slugInput.value) {
        titleInput.addEventListener('input', function () {
            slugInput.value = titleInput.value
                .toLowerCase()
                .normalize('NFD')
                .replace(/[\u0300-\u036f]/g, '')
                .replace(/[^a-z0-9]+/g, '-')
                .replace(/^-+|-+$/g, '');
        });
    }

    /* ── Preview d'image avant upload ── */
    document.querySelectorAll('input[type="file"][data-preview]').forEach(function (input) {
        input.addEventListener('change', function () {
            var previewId = input.getAttribute('data-preview');
            var preview = document.getElementById(previewId);
            if (preview && input.files && input.files[0]) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(input.files[0]);
            }
        });
    });

    /* ── Toggle du textarea riche (basique) ── */
    document.querySelectorAll('textarea[data-autoresize]').forEach(function (textarea) {
        function resize() {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }
        textarea.addEventListener('input', resize);
        resize();
    });

})();
