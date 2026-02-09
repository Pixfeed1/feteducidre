<?php
/**
 * Navigation principale — topbar + nav glassmorphism.
 * Menu dynamique basé sur les pages avec in_menu = 1, triées par menu_order.
 */
$baseUrl = \App\Core\Config::baseUrl();

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
$phoneClean = preg_replace('/[^0-9+]/', '', $phone);

// Récupérer HelloAsso URL
try {
    $helloassoRow = \App\Core\Database::getInstance()->fetch(
        "SELECT value FROM settings WHERE `group` = 'general' AND `key` = 'helloasso_url'"
    );
    $helloassoUrl = $helloassoRow['value'] ?? '';
} catch (\Exception) {
    $helloassoUrl = '';
}

// Logo SVG inline
$logoSvg = '<svg viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="28" cy="30" r="22" fill="#2C4A2E"/>
  <ellipse cx="28" cy="30" rx="16" ry="18" fill="#4A6B3E"/>
  <ellipse cx="28" cy="28" rx="10" ry="12" fill="#7A9E6B"/>
  <path d="M28 8 C26 4, 30 2, 32 6" stroke="#5C3D2E" stroke-width="2.5" stroke-linecap="round" fill="none"/>
  <ellipse cx="34" cy="10" rx="5" ry="3" fill="#7A9E6B" transform="rotate(30 34 10)"/>
</svg>';
?>

<!-- TOPBAR -->
<div class="topbar">
    <span>Association la Fête du Cidre — L'Hôtellerie de Flée, 49500</span>
    <a href="tel:<?= e($phoneClean) ?>">
        <?= icon('phone', 14) ?> <?= e($phone) ?>
    </a>
</div>

<!-- NAVIGATION -->
<nav class="main-nav" id="navbar">
    <div class="nav-inner">
        <a href="/" class="logo" aria-label="Fête du Cidre — Accueil">
            <div class="logo-icon"><?= $logoSvg ?></div>
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
