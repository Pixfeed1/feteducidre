<?php
/**
 * Layout principal de l'administration.
 * Variables attendues : $content (contenu de la page)
 */

$currentPath = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
$currentPath = rtrim($currentPath, '/') ?: '/';
$adminUser = $_SESSION['admin_user'] ?? [];

// Initiales pour l'avatar
$initials = mb_strtoupper(
    mb_substr($adminUser['first_name'] ?? '', 0, 1) . mb_substr($adminUser['last_name'] ?? '', 0, 1)
);

// Badge commandes en attente
$pendingOrders = $pendingOrders ?? 0;
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title><?= e($title ?? 'Administration') ?> — Fête du Cidre</title>
    <style><?= \App\Core\Theme::cssVariables() ?></style>
    <link rel="stylesheet" href="<?= asset('assets/css/admin.css') ?>">
</head>
<body class="admin-body">

    <!-- Barre latérale -->
    <aside class="admin-sidebar" id="adminSidebar">
        <div class="sidebar-header">
            <a href="/admin" class="sidebar-logo">
                <?= icon('apple', 24, '', '#A3C48E') ?>
            </a>
            <div class="sidebar-brand">Fête du Cidre <small>Administration</small></div>
            <button class="sidebar-close" id="sidebarClose" aria-label="Fermer le menu">
                <?= icon('x', 20) ?>
            </button>
        </div>

        <nav class="sidebar-nav">
            <span class="nav-label">Général</span>
            <a href="/admin/dashboard" class="nav-item <?= str_starts_with($currentPath, '/admin/dashboard') || $currentPath === '/admin' ? 'active' : '' ?>">
                <?= icon('layout-dashboard', 18) ?>
                <span>Tableau de bord</span>
            </a>

            <span class="nav-label">Contenu</span>
            <a href="/admin/pages" class="nav-item <?= str_starts_with($currentPath, '/admin/pages') ? 'active' : '' ?>">
                <?= icon('file-text', 18) ?>
                <span>Pages</span>
            </a>
            <a href="/admin/news" class="nav-item <?= str_starts_with($currentPath, '/admin/news') ? 'active' : '' ?>">
                <?= icon('newspaper', 18) ?>
                <span>Actualités</span>
            </a>
            <a href="/admin/albums" class="nav-item <?= str_starts_with($currentPath, '/admin/albums') ? 'active' : '' ?>">
                <?= icon('image', 18) ?>
                <span>Galerie photos</span>
            </a>
            <a href="/admin/editions" class="nav-item <?= str_starts_with($currentPath, '/admin/editions') ? 'active' : '' ?>">
                <?= icon('archive', 18) ?>
                <span>Archives</span>
            </a>

            <span class="nav-label">Boutique</span>
            <a href="/admin/products" class="nav-item <?= str_starts_with($currentPath, '/admin/products') ? 'active' : '' ?>">
                <?= icon('wine', 18) ?>
                <span>Produits</span>
            </a>
            <a href="/admin/orders" class="nav-item <?= str_starts_with($currentPath, '/admin/orders') ? 'active' : '' ?>">
                <?= icon('shopping-bag', 18) ?>
                <span>Commandes</span>
                <?php if ($pendingOrders > 0): ?>
                    <span class="nav-badge"><?= $pendingOrders ?></span>
                <?php endif; ?>
            </a>
            <a href="/admin/invoices" class="nav-item <?= str_starts_with($currentPath, '/admin/invoices') ? 'active' : '' ?>">
                <?= icon('receipt', 18) ?>
                <span>Factures</span>
            </a>

            <span class="nav-label">Événements</span>
            <a href="/admin/contests" class="nav-item <?= str_starts_with($currentPath, '/admin/contests') ? 'active' : '' ?>">
                <?= icon('trophy', 18) ?>
                <span>Concours</span>
            </a>
            <a href="/admin/hikes" class="nav-item <?= str_starts_with($currentPath, '/admin/hikes') ? 'active' : '' ?>">
                <?= icon('map', 18) ?>
                <span>Randonnées</span>
            </a>
            <a href="/admin/partners" class="nav-item <?= str_starts_with($currentPath, '/admin/partners') ? 'active' : '' ?>">
                <?= icon('heart', 18) ?>
                <span>Partenaires</span>
            </a>

            <span class="nav-label">Système</span>
            <a href="/admin/settings" class="nav-item <?= str_starts_with($currentPath, '/admin/settings') ? 'active' : '' ?>">
                <?= icon('settings', 18) ?>
                <span>Paramètres</span>
            </a>
            <a href="/admin/users" class="nav-item <?= str_starts_with($currentPath, '/admin/users') ? 'active' : '' ?>">
                <?= icon('users', 18) ?>
                <span>Utilisateurs</span>
            </a>
        </nav>

        <div class="sidebar-footer">
            <a class="sidebar-user" href="/admin/users/<?= (int) ($adminUser['id'] ?? 0) ?>/edit">
                <div class="user-avatar"><?= e($initials) ?></div>
                <div class="user-info">
                    <div class="user-name"><?= e(($adminUser['first_name'] ?? '') . ' ' . ($adminUser['last_name'] ?? '')) ?></div>
                    <div class="user-role"><?= ($adminUser['role'] ?? 'editor') === 'admin' ? 'Administrateur' : 'Éditeur' ?></div>
                </div>
            </a>
            <a class="logout-btn" href="/admin/logout">
                <?= icon('log-out', 16) ?>
                Se déconnecter
            </a>
        </div>
    </aside>

    <!-- Mobile backdrop -->
    <div class="sidebar-backdrop" id="sidebarBackdrop"></div>

    <!-- Contenu principal -->
    <div class="admin-main">
        <!-- Barre supérieure -->
        <header class="admin-topbar">
            <div class="topbar-left">
                <button class="topbar-toggle" id="sidebarToggle" aria-label="Ouvrir le menu">
                    <?= icon('menu', 22) ?>
                </button>
                <div class="topbar-search">
                    <span class="search-icon"><?= icon('search', 15) ?></span>
                    <input type="text" placeholder="Rechercher…" id="adminSearch">
                </div>
            </div>
            <div class="topbar-right">
                <button class="tb-btn" title="Notifications">
                    <?= icon('bell', 16) ?>
                    <?php if ($pendingOrders > 0): ?>
                        <span class="tb-dot"></span>
                    <?php endif; ?>
                </button>
                <a href="/" target="_blank" class="view-site">
                    <?= icon('external-link', 14) ?>
                    Voir le site
                </a>
            </div>
        </header>

        <!-- Zone de contenu -->
        <main class="admin-content">
            <?= flash('success') ?>
            <?= flash('error') ?>
            <?= flash('warning') ?>
            <?= flash('info') ?>
            <?= $content ?>
        </main>
    </div>

    <script>
    (function() {
        var sidebar = document.getElementById('adminSidebar');
        var toggle = document.getElementById('sidebarToggle');
        var close = document.getElementById('sidebarClose');
        var backdrop = document.getElementById('sidebarBackdrop');

        function openSidebar() {
            sidebar.classList.add('open');
            backdrop.classList.add('show');
        }

        function closeSidebar() {
            sidebar.classList.remove('open');
            backdrop.classList.remove('show');
        }

        if (toggle) toggle.addEventListener('click', openSidebar);
        if (close) close.addEventListener('click', closeSidebar);
        if (backdrop) backdrop.addEventListener('click', closeSidebar);
    })();
    </script>
    <script src="<?= asset('assets/js/admin.js') ?>" defer></script>
</body>
</html>
