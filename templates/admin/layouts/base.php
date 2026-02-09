<?php
/**
 * Layout principal de l'administration.
 * Variables attendues : $content (contenu de la page)
 */

$currentPath = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
$currentPath = rtrim($currentPath, '/') ?: '/';
$adminUser = $_SESSION['admin_user'] ?? [];
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
                <?= icon('apple', 28) ?>
                <span>Fête du Cidre</span>
            </a>
            <button class="sidebar-close" id="sidebarClose" aria-label="Fermer le menu">
                <?= icon('x', 20) ?>
            </button>
        </div>

        <nav class="sidebar-nav">
            <a href="/admin/dashboard" class="nav-link <?= str_starts_with($currentPath, '/admin/dashboard') || $currentPath === '/admin' ? 'active' : '' ?>">
                <?= icon('layout-dashboard', 20) ?>
                <span>Dashboard</span>
            </a>
            <a href="/admin/pages" class="nav-link <?= str_starts_with($currentPath, '/admin/pages') ? 'active' : '' ?>">
                <?= icon('file-text', 20) ?>
                <span>Pages</span>
            </a>
            <a href="/admin/products" class="nav-link <?= str_starts_with($currentPath, '/admin/products') ? 'active' : '' ?>">
                <?= icon('package', 20) ?>
                <span>Produits</span>
            </a>
            <a href="/admin/orders" class="nav-link <?= str_starts_with($currentPath, '/admin/orders') ? 'active' : '' ?>">
                <?= icon('shopping-cart', 20) ?>
                <span>Commandes</span>
            </a>
            <a href="/admin/invoices" class="nav-link <?= str_starts_with($currentPath, '/admin/invoices') ? 'active' : '' ?>">
                <?= icon('printer', 20) ?>
                <span>Factures</span>
            </a>
            <a href="/admin/albums" class="nav-link <?= str_starts_with($currentPath, '/admin/albums') ? 'active' : '' ?>">
                <?= icon('images', 20) ?>
                <span>Galerie</span>
            </a>
            <a href="/admin/editions" class="nav-link <?= str_starts_with($currentPath, '/admin/editions') ? 'active' : '' ?>">
                <?= icon('calendar', 20) ?>
                <span>Éditions</span>
            </a>
            <a href="/admin/contests" class="nav-link <?= str_starts_with($currentPath, '/admin/contests') ? 'active' : '' ?>">
                <?= icon('trophy', 20) ?>
                <span>Concours</span>
            </a>
            <a href="/admin/partners" class="nav-link <?= str_starts_with($currentPath, '/admin/partners') ? 'active' : '' ?>">
                <?= icon('heart', 20) ?>
                <span>Partenaires</span>
            </a>
            <a href="/admin/hikes" class="nav-link <?= str_starts_with($currentPath, '/admin/hikes') ? 'active' : '' ?>">
                <?= icon('mountain', 20) ?>
                <span>Randonnées</span>
            </a>
            <a href="/admin/settings" class="nav-link <?= str_starts_with($currentPath, '/admin/settings') ? 'active' : '' ?>">
                <?= icon('settings', 20) ?>
                <span>Paramètres</span>
            </a>
            <a href="/admin/users" class="nav-link <?= str_starts_with($currentPath, '/admin/users') ? 'active' : '' ?>">
                <?= icon('users', 20) ?>
                <span>Utilisateurs</span>
            </a>
        </nav>

        <div class="sidebar-footer">
            <a href="/" class="nav-link" target="_blank">
                <?= icon('external-link', 20) ?>
                <span>Voir le site</span>
            </a>
        </div>
    </aside>

    <!-- Contenu principal -->
    <div class="admin-main">
        <!-- Barre supérieure -->
        <header class="admin-topbar">
            <button class="topbar-toggle" id="sidebarToggle" aria-label="Ouvrir le menu">
                <?= icon('menu', 24) ?>
            </button>
            <div class="topbar-right">
                <span class="topbar-user">
                    <?= icon('user', 18) ?>
                    <?= e(($adminUser['first_name'] ?? '') . ' ' . ($adminUser['last_name'] ?? '')) ?>
                </span>
                <a href="/admin/logout" class="topbar-logout" title="Déconnexion">
                    <?= icon('log-out', 18) ?>
                    <span>Déconnexion</span>
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
    /* Script minimal pour le toggle du sidebar en responsive */
    (function() {
        const sidebar = document.getElementById('adminSidebar');
        const toggle = document.getElementById('sidebarToggle');
        const close = document.getElementById('sidebarClose');

        if (toggle) {
            toggle.addEventListener('click', function() {
                sidebar.classList.toggle('open');
            });
        }
        if (close) {
            close.addEventListener('click', function() {
                sidebar.classList.remove('open');
            });
        }
    })();
    </script>
    <script src="<?= asset('assets/js/admin.js') ?>" defer></script>
</body>
</html>
