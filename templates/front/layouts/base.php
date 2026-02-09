<?php
/**
 * Layout principal front — inclut head, nav, contenu, footer.
 * Variables attendues : $content, $seo, $page
 */
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <?php include dirname(__DIR__, 2) . '/partials/head.php'; ?>
</head>
<body>
    <?php include dirname(__DIR__, 2) . '/partials/nav.php'; ?>

    <main id="main" role="main">
        <?= flash('success') ?>
        <?= flash('error') ?>
        <?= flash('warning') ?>
        <?= $content ?>
    </main>

    <?php include dirname(__DIR__, 2) . '/partials/footer.php'; ?>

    <script defer src="<?= asset('assets/js/main.js') ?>"></script>
</body>
</html>
