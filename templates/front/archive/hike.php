<?php
/**
 * Template page Randonnées — Archives.
 * Variables : $seo, $classementYears (array year => [categories]), $reponseYears (int[])
 */
$catMeta = [
    'Adultes'   => ['class' => 'adultes',   'icon' => 'users'],
    'SuperCool' => ['class' => 'supercool', 'icon' => 'zap'],
    'Enfants'   => ['class' => 'enfants',   'icon' => 'baby'],
];
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
            <span aria-current="page">Randonnées</span>
        </nav>

        <span class="page-hero-badge">
            <?= icon('map', 14) ?> Parcours &amp; classements
        </span>

        <h1 class="page-hero-title" style="margin-left:auto;margin-right:auto">Les <em>randonnées</em></h1>

        <p class="page-hero-intro" style="margin-left:auto;margin-right:auto">Résultats, classements et réponses du rallye pédestre qui accompagne chaque édition de la Fête du Cidre.</p>
    </div>
</section>

<!-- Content -->
<section class="content-section">

    <!-- CLASSEMENTS -->
    <?php if (!empty($classementYears)): ?>
    <div class="block block-classements">
        <div class="block-header">
            <div class="block-icon">
                <?= icon('trophy', 26, '', 'var(--creme)') ?>
            </div>
            <div class="block-info">
                <h2>Résultats et classements</h2>
                <p>Trois catégories : Adultes, SuperCool et Enfants</p>
            </div>
        </div>

        <?php foreach ($classementYears as $year => $categories): ?>
            <div class="year-row">
                <div class="year-row-top">
                    <span class="year-pill"><?= (int) $year ?></span>
                    <span class="year-label">Classements</span>
                </div>
                <div class="year-links">
                    <?php foreach ($categories as $cat):
                        $meta = $catMeta[$cat] ?? ['class' => 'adultes', 'icon' => 'users'];
                    ?>
                        <a href="/randonnee/classement?year=<?= (int) $year ?>&cat=<?= urlencode($cat) ?>"
                           class="cat-link <?= $meta['class'] ?>">
                            <?= icon($meta['icon'], 14) ?> <?= e($cat) ?>
                        </a>
                    <?php endforeach; ?>
                </div>
            </div>
        <?php endforeach; ?>
    </div>
    <?php endif; ?>

    <!-- RÉPONSES -->
    <?php if (!empty($reponseYears)): ?>
    <div class="block block-reponses">
        <div class="block-header">
            <div class="block-icon">
                <?= icon('file-check', 26, '', 'white') ?>
            </div>
            <div class="block-info">
                <h2>Les réponses</h2>
                <p>Corrigés des questionnaires du rallye pédestre</p>
            </div>
        </div>
        <div class="reponses-grid">
            <?php foreach ($reponseYears as $year): ?>
                <a href="/randonnee/reponses?year=<?= (int) $year ?>" class="reponse-chip">
                    <span class="chip-year"><?= (int) $year ?></span>
                    <span class="chip-arrow"><?= icon('arrow-right', 14) ?></span>
                </a>
            <?php endforeach; ?>
        </div>
    </div>
    <?php endif; ?>

    <!-- STATISTIQUES -->
    <div class="block block-stats">
        <a href="/randonnee/classement" class="stats-card">
            <div class="stats-icon">
                <?= icon('bar-chart-3', 26, '', 'white') ?>
            </div>
            <div class="stats-text">
                <h3>Quelques statistiques</h3>
                <p>Chiffres et données sur les randonnées au fil des éditions</p>
            </div>
            <div class="stats-arrow">
                <?= icon('arrow-right', 20, '', 'var(--brun)') ?>
            </div>
        </a>
    </div>

    <?php if (empty($classementYears) && empty($reponseYears)): ?>
    <div style="text-align:center;padding:3rem 0">
        <div style="margin-bottom:1rem"><?= icon('map', 48, '', 'var(--vert-clair)') ?></div>
        <p style="font-size:1.1rem;color:var(--texte-leger)">Les résultats des prochaines randonnées seront disponibles ici.</p>
    </div>
    <?php endif; ?>

</section>
