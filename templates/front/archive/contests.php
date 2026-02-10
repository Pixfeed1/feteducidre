<?php
/**
 * Template page concours — vue palmarès par années.
 * Variables : $cidreYears, $affichesYears, $seo
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
            <span aria-current="page">Concours</span>
        </nav>

        <span class="page-hero-badge">
            <?= icon('award', 14) ?> Palmarès
        </span>

        <h1 class="page-hero-title" style="margin-left:auto;margin-right:auto">Les <em>concours</em></h1>

        <p class="page-hero-intro" style="margin-left:auto;margin-right:auto">Retrouvez les palmarès de chaque édition : concours du meilleur cidre, jus de pommes, pommeau et concours d'affiches.</p>
    </div>
</section>

<!-- Contenu concours -->
<section class="concours-content">

    <!-- Concours du meilleur cidre -->
    <?php if (!empty($cidreYears)): ?>
    <div class="concours-type type-cidre">
        <div class="type-header">
            <div class="type-icon">
                <?= icon('trophy', 26) ?>
            </div>
            <div class="type-info">
                <h2>Concours du meilleur cidre</h2>
                <p>Cidre, jus de pommes et pommeau</p>
            </div>
        </div>
        <div class="years-grid">
            <?php foreach ($cidreYears as $i => $year): ?>
                <a href="/concours/palmares?year=<?= (int) $year ?>"
                   class="year-card<?= $i === 0 ? ' featured' : '' ?>">
                    <div>
                        <?php if ($i === 0): ?>
                            <span class="featured-label">Dernier palmarès</span>
                        <?php endif; ?>
                        <span class="year-badge"><?= (int) $year ?></span>
                    </div>
                    <div class="year-arrow">
                        <?= icon('arrow-right', $i === 0 ? 20 : 16) ?>
                    </div>
                </a>
            <?php endforeach; ?>
        </div>
    </div>
    <?php endif; ?>

    <!-- Concours d'affiches -->
    <?php if (!empty($affichesYears)): ?>
    <div class="concours-type type-affiches">
        <div class="type-header">
            <div class="type-icon">
                <?= icon('image', 26) ?>
            </div>
            <div class="type-info">
                <h2>Concours d'affiches</h2>
                <p>Création graphique pour la Fête du Cidre</p>
            </div>
        </div>
        <div class="years-grid">
            <?php foreach ($affichesYears as $year): ?>
                <a href="/concours/palmares?year=<?= (int) $year ?>" class="year-card">
                    <span class="year-badge"><?= (int) $year ?></span>
                    <div class="year-arrow">
                        <?= icon('arrow-right', 16) ?>
                    </div>
                </a>
            <?php endforeach; ?>
        </div>
    </div>
    <?php endif; ?>

    <!-- État vide -->
    <?php if (empty($cidreYears) && empty($affichesYears)): ?>
        <div style="text-align:center;padding:4rem 0">
            <?= icon('trophy', 48, '', 'var(--vert-clair)') ?>
            <h2 style="margin-top:1rem">Aucun palmarès disponible</h2>
            <p style="color:var(--brun);margin-top:.5rem">Les résultats des concours seront bientôt en ligne.</p>
            <a href="/concours/inscription" class="btn btn-primary" style="margin-top:1.5rem">
                <?= icon('edit', 18) ?> S'inscrire au concours
            </a>
        </div>
    <?php endif; ?>

</section>
