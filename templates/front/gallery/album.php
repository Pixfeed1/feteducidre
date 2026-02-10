<?php
/**
 * Template détail d'un album photo — masonry grid + lightbox.
 * Variables : $album, $photos, $seo
 */
$baseUrl = \App\Core\Config::baseUrl();
$totalPhotos = count($photos);
$typeMeta = [
    'fete'     => ['icon' => 'party-popper', 'label' => 'Fête'],
    'rallye'   => ['icon' => 'map',          'label' => 'Rallye'],
    'affiches' => ['icon' => 'image',        'label' => 'Affiches'],
    'general'  => ['icon' => 'calendar',     'label' => 'Édition'],
];
$type = $album['type'] ?? 'general';
$meta = $typeMeta[$type] ?? $typeMeta['general'];
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
            <a href="/galerie">Galerie Photos</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <span aria-current="page"><?= e($album['title']) ?></span>
        </nav>

        <span class="page-hero-badge">
            <?= icon('camera', 14) ?> Album photo
        </span>

        <h1 class="page-hero-title" style="margin-left:auto;margin-right:auto"><?= e($album['title']) ?></h1>

        <?php if ($album['description']): ?>
            <p class="page-hero-intro" style="margin-left:auto;margin-right:auto"><?= e($album['description']) ?></p>
        <?php endif; ?>

        <div class="hero-meta">
            <?php if ($totalPhotos > 0): ?>
                <div class="hero-meta-item">
                    <?= icon('image', 16) ?>
                    <strong><?= $totalPhotos ?></strong> photo<?= $totalPhotos > 1 ? 's' : '' ?>
                </div>
            <?php endif; ?>
            <?php if ($album['year']): ?>
                <div class="hero-meta-item">
                    <?= icon('calendar', 16) ?>
                    <?= (int) $album['year'] ?>
                </div>
            <?php endif; ?>
            <div class="hero-meta-item">
                <?= icon($meta['icon'], 16) ?>
                <?= e($meta['label']) ?>
            </div>
        </div>
    </div>
</section>

<!-- Toolbar -->
<div class="toolbar">
    <div class="toolbar-inner">
        <div class="toolbar-info">
            <?= icon('image', 16, '', 'var(--vert-clair)') ?>
            <strong><?= $totalPhotos ?></strong> photo<?= $totalPhotos > 1 ? 's' : '' ?> — <span>Cliquez pour agrandir</span>
        </div>
        <div class="toolbar-actions">
            <a href="/galerie" class="tb-btn">
                <?= icon('arrow-left', 14) ?> Retour
            </a>
        </div>
    </div>
</div>

<!-- Gallery Grid -->
<section class="gallery-section">
    <?php if (empty($photos)): ?>
        <div style="text-align:center;padding:4rem 0">
            <div style="margin-bottom:1rem"><?= icon('image', 48, '', 'var(--vert-clair)') ?></div>
            <h2 style="margin-bottom:.5rem">Aucune photo dans cet album</h2>
            <p style="color:var(--texte-leger)">Les photos seront bientôt en ligne.</p>
        </div>
    <?php else: ?>
        <div class="masonry" id="masonry">
            <?php foreach ($photos as $index => $photo): ?>
                <div class="photo-item" data-index="<?= $index ?>"
                     data-src="<?= e($baseUrl . '/storage/uploads/large/' . $photo['filename']) ?>">
                    <div class="photo-inner">
                        <?php if ($photo['image']): ?>
                            <?= img($photo['image'], $photo['title'] ?? $album['title']) ?>
                        <?php else: ?>
                            <div style="background:var(--creme-fonce);height:200px;display:flex;align-items:center;justify-content:center">
                                <?= icon('image', 32, '', 'var(--vert-clair)') ?>
                            </div>
                        <?php endif; ?>
                        <div class="photo-hover">
                            <span class="photo-index"><?= $index + 1 ?> / <?= $totalPhotos ?></span>
                            <span class="photo-zoom"><?= icon('maximize', 14) ?></span>
                        </div>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>
</section>

<!-- Lightbox -->
<?php if (!empty($photos)): ?>
<div class="lightbox" id="lightbox">
    <button class="lb-close" id="lbClose">
        <?= icon('x', 20) ?>
    </button>
    <button class="lb-nav lb-prev" id="lbPrev">
        <?= icon('chevron-left', 22) ?>
    </button>
    <div class="lb-image-wrap" id="lbImageWrap"></div>
    <button class="lb-nav lb-next" id="lbNext">
        <?= icon('chevron-right', 22) ?>
    </button>
    <div class="lb-footer">
        <span class="lb-counter" id="lbCounter">1 / <?= $totalPhotos ?></span>
    </div>
</div>

<script>
(function() {
    var items = document.querySelectorAll('.photo-item');
    var lightbox = document.getElementById('lightbox');
    var wrap = document.getElementById('lbImageWrap');
    var counter = document.getElementById('lbCounter');
    var total = items.length;
    var current = 0;

    function openLB(idx) {
        current = idx;
        updateLB();
        lightbox.classList.add('open');
        document.body.classList.add('lb-open');
    }

    function closeLB() {
        lightbox.classList.remove('open');
        document.body.classList.remove('lb-open');
    }

    function navigate(dir) {
        current = (current + dir + total) % total;
        updateLB();
    }

    function updateLB() {
        var item = items[current];
        var src = item.dataset.src;
        var img = item.querySelector('img');
        var alt = img ? img.alt : '';
        wrap.innerHTML = '<img src="' + src + '" alt="' + alt + '">';
        counter.textContent = (current + 1) + ' / ' + total;
    }

    items.forEach(function(item, i) {
        item.addEventListener('click', function() { openLB(i); });
    });

    document.getElementById('lbClose').addEventListener('click', closeLB);
    document.getElementById('lbPrev').addEventListener('click', function() { navigate(-1); });
    document.getElementById('lbNext').addEventListener('click', function() { navigate(1); });

    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) closeLB();
    });

    document.addEventListener('keydown', function(e) {
        if (!lightbox.classList.contains('open')) return;
        if (e.key === 'Escape') closeLB();
        if (e.key === 'ArrowLeft') navigate(-1);
        if (e.key === 'ArrowRight') navigate(1);
    });
})();
</script>
<?php endif; ?>
