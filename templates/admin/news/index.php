<?php
/**
 * Page d'administration des Actualités — redirection externe et options menu.
 * Variables : $settings (tableau clé/valeur)
 */
$url       = $settings['redirect_url'] ?? '';
$newTab    = ($settings['open_new_tab'] ?? '1') === '1';
$visible   = ($settings['show_in_menu'] ?? '1') === '1';
$label     = $settings['menu_label'] ?? 'Actualités';
?>

<div style="max-width:700px">

    <div class="page-header-with-icon">
        <div class="page-icon" style="background:var(--orange-cidre)"><?= icon('newspaper', 22, '', 'white') ?></div>
        <h1>Actualités</h1>
    </div>

    <form method="post" action="/admin/news" id="newsForm">
        <?= csrf_field() ?>

        <div class="setting-card">

            <!-- Redirection -->
            <div class="card-section">
                <div class="card-section-label"><?= icon('external-link', 12) ?> Redirection externe</div>
                <div class="card-section-desc">Le lien « Actualités » du menu redirige les visiteurs vers une page externe. Modifiez l'URL ci-dessous si nécessaire.</div>

                <div class="field">
                    <label for="redirectUrl">URL de redirection</label>
                    <input type="url" id="redirectUrl" name="redirect_url" value="<?= e($url) ?>" placeholder="https://...">
                    <div class="field-hint"><?= icon('info', 12) ?> Les visiteurs seront redirigés vers cette URL en cliquant sur « Actualités »</div>
                </div>

                <div class="url-preview">
                    <?= icon('globe', 16, '', 'var(--texte-leger)') ?>
                    <a href="<?= e($url) ?>" target="_blank" class="url-preview-link" id="previewLink"><?= e($url ?: 'Aucune URL définie') ?></a>
                    <button type="button" class="test-btn" onclick="testUrl()"><?= icon('external-link', 12) ?> Tester</button>
                </div>
            </div>

            <!-- Options -->
            <div class="card-section">
                <div class="card-section-label"><?= icon('settings-2', 12) ?> Options</div>

                <div class="toggle-row">
                    <div class="toggle-row-left">
                        <span class="toggle-row-label">Ouvrir dans un nouvel onglet</span>
                        <span class="toggle-row-desc">Le lien s'ouvre dans un nouvel onglet du navigateur</span>
                    </div>
                    <div class="toggle <?= $newTab ? 'active' : '' ?>" id="toggleNewTab" data-field="open_new_tab"></div>
                </div>

                <div class="toggle-row" style="margin-top:0.5rem">
                    <div class="toggle-row-left">
                        <span class="toggle-row-label">Afficher dans le menu</span>
                        <span class="toggle-row-desc">Masquer temporairement le lien de la navigation</span>
                    </div>
                    <div class="toggle <?= $visible ? 'active' : '' ?>" id="toggleVisible" data-field="show_in_menu"></div>
                </div>

                <!-- Hidden inputs synchronisés par JS -->
                <input type="hidden" name="open_new_tab" id="fieldNewTab" value="<?= $newTab ? '1' : '' ?>">
                <input type="hidden" name="show_in_menu" id="fieldVisible" value="<?= $visible ? '1' : '' ?>">
            </div>

            <!-- Label -->
            <div class="card-section">
                <div class="card-section-label"><?= icon('type', 12) ?> Affichage</div>
                <div class="field">
                    <label for="menuLabel">Libellé dans le menu</label>
                    <input type="text" id="menuLabel" name="menu_label" value="<?= e($label) ?>">
                    <div class="field-hint"><?= icon('info', 12) ?> Texte affiché dans la barre de navigation du site</div>
                </div>
            </div>

        </div>

        <div class="save-bar">
            <button type="submit" class="btn btn-primary"><?= icon('check', 16) ?> Enregistrer</button>
        </div>
    </form>

</div>

<!-- Toast -->
<div class="toast" id="toast"><?= icon('check-circle', 16) ?> <span id="toastMsg">Enregistré</span></div>

<script>
(function() {
    // Toggle switches
    document.querySelectorAll('.toggle[data-field]').forEach(function(toggle) {
        var fieldName = toggle.dataset.field;
        var hidden = document.querySelector('input[name="' + fieldName + '"]');
        toggle.addEventListener('click', function() {
            this.classList.toggle('active');
            hidden.value = this.classList.contains('active') ? '1' : '';
        });
    });

    // Live URL preview
    var urlInput = document.getElementById('redirectUrl');
    var previewLink = document.getElementById('previewLink');
    if (urlInput && previewLink) {
        urlInput.addEventListener('input', function() {
            previewLink.href = this.value;
            previewLink.textContent = this.value || 'Aucune URL définie';
        });
    }
})();

// Test URL
function testUrl() {
    var url = document.getElementById('redirectUrl').value;
    if (url) window.open(url, '_blank');
}
</script>
