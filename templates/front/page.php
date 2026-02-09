<?php
/**
 * Template page générique.
 * Affiche le contenu d'une page CMS (origines, infos pratiques, etc.)
 * Variables : $page, $seo
 */
?>

<!-- Fil d'Ariane -->
<section class="breadcrumb-section">
    <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane">
            <a href="/">Accueil</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <span aria-current="page"><?= e($page['title'] ?? '') ?></span>
        </nav>
    </div>
</section>

<!-- En-tête de page -->
<section class="page-header">
    <div class="container">
        <h1><?= e($page['title'] ?? '') ?></h1>
        <?php if (!empty($page['excerpt'])): ?>
            <p><?= e($page['excerpt']) ?></p>
        <?php endif; ?>
    </div>
</section>

<!-- Contenu de la page -->
<section class="section section-page-content">
    <div class="container" style="max-width:900px">
        <div class="page-body" style="line-height:1.8">
            <?php if (!empty($page['content'])): ?>
                <?= sanitize($page['content']) ?>
            <?php else: ?>
                <div class="empty-state" style="text-align:center;padding:4rem 0">
                    <?= icon('file-text', 48, '', 'var(--vert-clair)') ?>
                    <p style="margin-top:1rem;color:var(--brun)">Cette page est en cours de rédaction.</p>
                </div>
            <?php endif; ?>
        </div>
    </div>
</section>
