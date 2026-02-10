<?php
/**
 * Template page Programmes / Flyers des éditions.
 * Variables : $editions, $seo
 */
$latest = !empty($editions) ? $editions[0] : null;
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
            <span aria-current="page">Programmes</span>
        </nav>

        <span class="page-hero-badge">
            <?= icon('book-open', 14) ?> Flyers &amp; programmes
        </span>

        <h1 class="page-hero-title" style="margin-left:auto;margin-right:auto">Les <em>programmes</em></h1>

        <p class="page-hero-intro" style="margin-left:auto;margin-right:auto">Retrouvez les différents programmes et flyers des éditions passées de la Fête du Cidre.</p>
    </div>
</section>

<!-- Contenu -->
<section class="content-section">

    <!-- Bloc Programmes -->
    <div class="block block-programmes">
        <div class="block-header">
            <div class="block-icon">
                <?= icon('file-text', 24) ?>
            </div>
            <div class="block-info">
                <h2>Les programmes au fil du temps</h2>
                <p>Cliquez sur une édition pour découvrir son programme</p>
            </div>
        </div>

        <?php if (empty($editions)): ?>
            <div style="text-align:center;padding:3rem 0">
                <?= icon('calendar', 48, '', 'var(--vert-clair)') ?>
                <p style="margin-top:1rem;color:var(--brun)">Aucun programme disponible pour le moment.</p>
            </div>
        <?php else: ?>
            <div class="editions-grid">
                <?php foreach ($editions as $i => $edition): ?>
                    <a href="/archives/<?= (int) $edition['year'] ?>"
                       class="pgm-card<?= $i === 0 ? ' featured' : '' ?>">
                        <div class="pgm-icon">
                            <?php if ($i === 0): ?>
                                <?= icon('star', 18, '', 'var(--orange-cidre)') ?>
                            <?php else: ?>
                                <?= icon('file-text', 18, '', 'var(--vert-mousse)') ?>
                            <?php endif; ?>
                        </div>
                        <span class="edition-year"><?= (int) $edition['year'] ?></span>
                        <span class="pgm-label">
                            <?= icon('download', 10) ?>
                            <?= $i === 0 ? 'Dernier programme' : 'Programme' ?>
                        </span>
                    </a>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </div>

    <!-- Bloc Thèmes -->
    <div class="block block-themes">
        <a href="/archives" class="themes-card">
            <div class="themes-icon">
                <?= icon('palette', 26) ?>
            </div>
            <div class="themes-text">
                <h3>Les thèmes depuis le début</h3>
                <p>Retrouvez la liste complète des thèmes depuis la création de la Fête du Cidre</p>
            </div>
            <div class="themes-arrow">
                <?= icon('arrow-right', 20) ?>
            </div>
        </a>
    </div>

</section>
