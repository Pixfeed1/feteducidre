<?php
/**
 * Template page générique (origines, infos pratiques, mentions légales, etc.)
 * Design premium avec page-hero + contenu CMS riche.
 * Variables : $page, $seo
 */
?>

<!-- Page Hero -->
<section class="page-hero">
    <div class="page-hero-pattern"></div>
    <div class="page-hero-decoration"></div>
    <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane">
            <a href="/">Accueil</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <span aria-current="page"><?= e($page['title'] ?? '') ?></span>
        </nav>

        <span class="page-hero-badge">
            <?= icon('book-open', 16) ?> <?= e($page['title'] ?? '') ?>
        </span>

        <h1 class="page-hero-title"><?= $page['title'] ?? '' ?></h1>

        <?php if (!empty($page['excerpt'])): ?>
            <p class="page-hero-intro"><?= e($page['excerpt']) ?></p>
        <?php endif; ?>
    </div>
</section>

<!-- Contenu CMS -->
<section class="section">
    <div class="container cms-content">
        <?php if (!empty($page['content'])): ?>
            <?= sanitize($page['content']) ?>
        <?php else: ?>
            <div class="empty-state" style="text-align:center;padding:4rem 0">
                <?= icon('file-text', 48, '', 'var(--vert-clair)') ?>
                <p style="margin-top:1rem;color:var(--brun)">Cette page est en cours de rédaction.</p>
            </div>
        <?php endif; ?>
    </div>
</section>
