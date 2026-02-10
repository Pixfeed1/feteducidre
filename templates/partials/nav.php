<?php
/**
 * Navigation principale — topbar + nav glassmorphism.
 * Menu dynamique basé sur les pages avec in_menu = 1, triées par menu_order.
 */
// Récupérer les pages du menu
try {
    $menuPages = \App\Core\Database::getInstance()->fetchAll(
        "SELECT title, slug FROM pages WHERE in_menu = 1 AND status = 'published' ORDER BY menu_order ASC"
    );
} catch (\Exception) {
    $menuPages = [];
}

// Récupérer le téléphone depuis les settings
try {
    $phoneRow = \App\Core\Database::getInstance()->fetch(
        "SELECT value FROM settings WHERE `group` = 'general' AND `key` = 'association_phone'"
    );
    $phone = $phoneRow['value'] ?? '06.79.96.87.54';
} catch (\Exception) {
    $phone = '06.79.96.87.54';
}
$phoneClean = phone_clean($phone);

// Récupérer HelloAsso URL
try {
    $helloassoRow = \App\Core\Database::getInstance()->fetch(
        "SELECT value FROM settings WHERE `group` = 'general' AND `key` = 'helloasso_url'"
    );
    $helloassoUrl = $helloassoRow['value'] ?? '';
} catch (\Exception) {
    $helloassoUrl = '';
}

// Récupérer les paramètres Actualités (redirection externe)
try {
    $newsRows = \App\Core\Database::getInstance()->fetchAll(
        "SELECT `key`, value FROM settings WHERE `group` = 'news'"
    );
    $newsSettings = [];
    foreach ($newsRows as $nr) {
        $newsSettings[$nr['key']] = $nr['value'];
    }
} catch (\Exception) {
    $newsSettings = [];
}
$newsUrl     = $newsSettings['redirect_url'] ?? '';
$newsLabel   = $newsSettings['menu_label'] ?? 'Actualités';
$newsVisible = ($newsSettings['show_in_menu'] ?? '1') === '1';
$newsNewTab  = ($newsSettings['open_new_tab'] ?? '1') === '1';

?>

<!-- TOPBAR -->
<div class="topbar-wrap">
  <div class="topbar">
    <span>Association la Fête du Cidre — L'Hôtellerie de Flée, 49500</span>
    <a href="tel:<?= e($phoneClean) ?>">
        <?= icon('phone', 14) ?> <?= e($phone) ?>
    </a>
  </div>
</div>

<!-- NAVIGATION -->
<nav class="main-nav" id="navbar">
    <div class="nav-inner">
        <a href="/" class="logo" aria-label="Fête du Cidre — Accueil">
            <div class="logo-icon"><img src="/assets/images/logo.png" alt="Fête du Cidre" width="80" height="80"></div>
            <div class="logo-text">
                Fête du Cidre
                <span>L'Hôtellerie de Flée</span>
            </div>
        </a>

        <ul class="nav-links" id="navLinks">
            <?php foreach ($menuPages as $mp): ?>
                <?php if ($mp['slug'] === 'accueil') continue; ?>
                <li>
                    <a href="/<?= e($mp['slug']) ?>"
                       class="<?= active('/' . $mp['slug']) ?>">
                        <?= e($mp['title']) ?>
                    </a>
                </li>
            <?php endforeach; ?>
            <?php if ($newsVisible && $newsUrl): ?>
                <li>
                    <a href="<?= e($newsUrl) ?>"<?= $newsNewTab ? ' target="_blank" rel="noopener"' : '' ?>>
                        <?= e($newsLabel) ?>
                    </a>
                </li>
            <?php endif; ?>
            <?php if ($helloassoUrl): ?>
                <li>
                    <a href="<?= e($helloassoUrl) ?>" class="active" target="_blank" rel="noopener">
                        Réserver
                    </a>
                </li>
            <?php endif; ?>
        </ul>

        <button class="menu-toggle" id="menuToggle" aria-label="Menu">
            <span></span><span></span><span></span>
        </button>
    </div>
</nav>
