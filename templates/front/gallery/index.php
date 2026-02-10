<?php
/**
 * Template Galerie Photos — Albums groupés par année avec filtre par type.
 * Variables : $albumsByYear (array year => albums[]), $types (string[]), $seo
 */
$typeMeta = [
    'fete'     => ['icon' => 'party-popper', 'label' => 'Fête'],
    'rallye'   => ['icon' => 'map',          'label' => 'Rallye'],
    'affiches' => ['icon' => 'image',        'label' => 'Affiches'],
    'general'  => ['icon' => 'calendar',     'label' => 'Édition'],
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
            <span aria-current="page">Galerie Photos</span>
        </nav>

        <span class="page-hero-badge">
            <?= icon('camera', 14) ?> Souvenirs
        </span>

        <h1 class="page-hero-title" style="margin-left:auto;margin-right:auto">Galerie <em>photos</em></h1>

        <p class="page-hero-intro" style="margin-left:auto;margin-right:auto">Retrouvez les photos des différentes éditions… depuis l'âge de la photo numérique.</p>
    </div>
</section>

<!-- Filter bar -->
<?php if (count($types) > 1): ?>
<div class="filter-bar">
    <div class="filter-inner">
        <button class="filter-btn active" data-filter="all">
            <?= icon('grid-3x3', 13) ?> Tout
        </button>
        <?php foreach ($types as $type):
            $meta = $typeMeta[$type] ?? $typeMeta['general'];
        ?>
            <button class="filter-btn" data-filter="<?= e($type) ?>">
                <?= icon($meta['icon'], 13) ?> <?= e($meta['label']) ?>
            </button>
        <?php endforeach; ?>
    </div>
</div>
<?php endif; ?>

<!-- Albums -->
<section class="albums-section" id="albumsSection">
    <?php if (empty($albumsByYear)): ?>
        <div style="text-align:center;padding:4rem 0">
            <div style="margin-bottom:1rem"><?= icon('camera', 48, '', 'var(--vert-clair)') ?></div>
            <h2 style="margin-bottom:.5rem">Aucun album disponible</h2>
            <p style="color:var(--texte-leger)">Les photos seront bientôt en ligne. Revenez nous voir !</p>
        </div>
    <?php else: ?>
        <?php foreach ($albumsByYear as $year => $albums): ?>
            <div class="year-group">
                <div class="year-group-label"><h2><?= (int) $year ?></h2></div>
                <div class="albums-row">
                    <?php foreach ($albums as $album):
                        $type = $album['type'] ?: 'general';
                        $meta = $typeMeta[$type] ?? $typeMeta['general'];
                    ?>
                        <a href="/galerie/<?= e($album['slug']) ?>"
                           class="album-card" data-type="<?= e($type) ?>">
                            <div class="album-bg">
                                <?php if (!empty($album['cover_image'])): ?>
                                    <?= img($album['cover_image'], $album['title'], 'album-bg-img') ?>
                                <?php endif; ?>
                            </div>
                            <div class="album-overlay">
                                <span class="album-type-badge">
                                    <?= icon($meta['icon'], 10) ?> <?= e($meta['label']) ?>
                                </span>
                                <?php if ($album['photo_count'] > 0): ?>
                                    <span class="album-photo-count">
                                        <?= icon('image', 10) ?> <?= (int) $album['photo_count'] ?>
                                    </span>
                                <?php endif; ?>
                                <span class="album-title"><?= e($album['title']) ?></span>
                                <?php if (!empty($album['description'])): ?>
                                    <span class="album-subtitle"><?= e(truncate($album['description'], 40)) ?></span>
                                <?php endif; ?>
                                <span class="album-arrow"><?= icon('arrow-right', 14) ?></span>
                            </div>
                        </a>
                    <?php endforeach; ?>
                </div>
            </div>
        <?php endforeach; ?>
    <?php endif; ?>
</section>

<?php if (!empty($albumsByYear) && count($types) > 1): ?>
<script>
document.addEventListener('DOMContentLoaded', function() {
    var btns = document.querySelectorAll('.filter-btn');
    btns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            btns.forEach(function(b) { b.classList.remove('active'); });
            btn.classList.add('active');
            var type = btn.dataset.filter;
            document.querySelectorAll('.album-card').forEach(function(card) {
                card.style.display = (type === 'all' || card.dataset.type === type) ? '' : 'none';
            });
            document.querySelectorAll('.year-group').forEach(function(group) {
                var cards = group.querySelectorAll('.album-card');
                var anyVisible = false;
                cards.forEach(function(c) { if (c.style.display !== 'none') anyVisible = true; });
                group.style.display = anyVisible ? '' : 'none';
            });
        });
    });
});
</script>
<?php endif; ?>
