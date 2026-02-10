<?php
/**
 * Template dédié — Nos Origines.
 * Contenu CMS riche avec styles article (timeline, chapeau, etc.)
 * Variables : $page, $seo
 */
?>

<!-- Page Hero -->
<section class="page-hero" style="text-align:center">
    <div class="page-hero-pattern"></div>
    <div class="page-hero-decoration"></div>
    <div class="page-hero-content" style="position:relative;z-index:2;max-width:700px;margin:0 auto;padding:5rem 2rem 4rem">
        <nav class="breadcrumb" style="justify-content:center;margin-bottom:1.5rem" aria-label="Fil d'Ariane">
            <a href="/">Accueil</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <a href="/archives">Revivez les années</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <span aria-current="page">Origines</span>
        </nav>

        <span class="page-hero-badge">
            <?= icon('history', 14) ?> Depuis 1977
        </span>

        <h1 class="page-hero-title" style="margin-left:auto;margin-right:auto">Les <em>origines</em></h1>

        <?php if (!empty($page['excerpt'])): ?>
            <p class="page-hero-intro" style="margin-left:auto;margin-right:auto"><?= e($page['excerpt']) ?></p>
        <?php else: ?>
            <p class="page-hero-intro" style="margin-left:auto;margin-right:auto">De la première Foire au Cidre à l'événement incontournable du Haut Anjou : retour sur près de 50 ans d'histoire.</p>
        <?php endif; ?>
    </div>
</section>

<!-- Article CMS -->
<article class="article-wrapper">
    <div class="cms-content">
        <?php if (!empty($page['content'])): ?>
            <?= sanitize($page['content']) ?>
        <?php else: ?>
            <div class="empty-state" style="text-align:center;padding:4rem 0">
                <?= icon('file-text', 48, '', 'var(--vert-clair)') ?>
                <p style="margin-top:1rem;color:var(--brun)">Cette page est en cours de rédaction.</p>
            </div>
        <?php endif; ?>
    </div>
</article>
