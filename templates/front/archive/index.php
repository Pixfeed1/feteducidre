<?php
/**
 * Template Archives — page d'accueil "Revivez les années".
 * Navigation vers les différentes sections d'archives.
 * Variables : $page, $seo
 */
$cards = [
    [
        'icon'  => 'book-open',
        'label' => 'Histoire',
        'title' => 'Origines',
        'desc'  => 'Découvrez comment tout a commencé en 1989 et l\'histoire de notre fête.',
        'href'  => '/origines',
    ],
    [
        'icon'  => 'image',
        'label' => 'Collection',
        'title' => 'Affiches',
        'desc'  => 'Les affiches de chaque édition.',
        'href'  => '/archives/programmes',
    ],
    [
        'icon'  => 'map',
        'label' => 'Parcours',
        'title' => 'Randonnées',
        'desc'  => 'Classements et parcours.',
        'href'  => '/randonnee',
    ],
    [
        'icon'  => 'clipboard-list',
        'label' => 'Éditions',
        'title' => 'Programmes',
        'desc'  => 'Les programmes année par année.',
        'href'  => '/archives/programmes',
    ],
    [
        'icon'  => 'camera',
        'label' => 'Souvenirs',
        'title' => 'Photos',
        'desc'  => 'Albums et galeries photo.',
        'href'  => '/galerie',
    ],
    [
        'icon'  => 'award',
        'label' => 'Compétition',
        'title' => 'Concours',
        'desc'  => 'Résultats et inscriptions.',
        'href'  => '/concours',
    ],
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
            <span aria-current="page">Revivez les années</span>
        </nav>

        <span class="page-hero-badge">
            <?= icon('archive', 14) ?> Souvenirs
        </span>

        <h1 class="page-hero-title" style="margin-left:auto;margin-right:auto">Revivez les <em>années</em></h1>

        <p class="page-hero-intro" style="margin-left:auto;margin-right:auto">Depuis 1989, la Fête du Cidre célèbre chaque année le terroir et le savoir-faire du Haut Anjou. Plongez dans nos archives.</p>
    </div>
</section>

<?php if (!empty($page['content'])): ?>
<section class="section" style="padding-bottom:0">
    <div class="container cms-content">
        <?= sanitize($page['content']) ?>
    </div>
</section>
<?php endif; ?>

<!-- Archive Cards -->
<section class="arc-landing">
    <div class="arc-grid">
        <?php foreach ($cards as $card): ?>
            <a href="<?= $card['href'] ?>" class="arc-card">
                <div class="arc-card-bg"></div>
                <div class="arc-card-content">
                    <div class="arc-card-icon">
                        <?= icon($card['icon'], 24) ?>
                    </div>
                    <span class="arc-card-label"><?= $card['label'] ?></span>
                    <span class="arc-card-title"><?= $card['title'] ?></span>
                    <span class="arc-card-desc"><?= $card['desc'] ?></span>
                </div>
                <div class="arc-card-arrow">
                    <?= icon('arrow-up-right', 16) ?>
                </div>
            </a>
        <?php endforeach; ?>
    </div>
</section>
