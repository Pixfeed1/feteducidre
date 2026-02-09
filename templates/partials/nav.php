<?php
/**
 * Navigation principale du site.
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

// Compter le panier
$cartCount = 0;
if (!empty($_SESSION['cart'])) {
    foreach ($_SESSION['cart'] as $item) {
        $cartCount += (int)($item['quantity'] ?? 0);
    }
}
?>
<header class="site-header" id="header">
    <div class="container">
        <nav class="nav" role="navigation" aria-label="Navigation principale">
            <a href="/" class="nav-logo" aria-label="Fête du Cidre — Accueil">
                <span class="nav-logo-text">Fête du Cidre</span>
            </a>

            <ul class="nav-menu" id="nav-menu">
                <li><a href="/" class="nav-link <?= active('/') ?>">Accueil</a></li>
                <?php foreach ($menuPages as $mp): ?>
                    <?php if ($mp['slug'] === 'accueil') continue; ?>
                    <li>
                        <a href="/<?= e($mp['slug']) ?>"
                           class="nav-link <?= active('/' . $mp['slug']) ?>">
                            <?= e($mp['title']) ?>
                        </a>
                    </li>
                <?php endforeach; ?>
            </ul>

            <div class="nav-actions">
                <a href="/panier" class="nav-cart" aria-label="Panier (<?= $cartCount ?> articles)">
                    <?= icon('shopping-cart', 22) ?>
                    <?php if ($cartCount > 0): ?>
                        <span class="nav-cart-badge"><?= $cartCount ?></span>
                    <?php endif; ?>
                </a>

                <button class="nav-toggle" id="nav-toggle" aria-label="Menu" aria-expanded="false">
                    <?= icon('menu', 24) ?>
                </button>
            </div>
        </nav>
    </div>
</header>
