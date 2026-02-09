<?php
/**
 * Template détail d'un album photo.
 * Variables : $album, $photos, $seo
 */
$baseUrl = \App\Core\Config::baseUrl();
?>

<!-- Fil d'Ariane -->
<section class="breadcrumb-section">
    <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane">
            <a href="/">Accueil</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <a href="/galerie">Galerie</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <span aria-current="page"><?= e($album['title']) ?></span>
        </nav>
    </div>
</section>

<!-- En-tête de l'album -->
<section class="page-header" style="padding-bottom:1rem">
    <div class="container">
        <h1><?= e($album['title']) ?></h1>
        <?php if ($album['year']): ?>
            <p><?= icon('calendar', 18) ?> Édition <?= (int) $album['year'] ?></p>
        <?php endif; ?>
        <?php if ($album['description']): ?>
            <p style="margin-top:.75rem;max-width:700px"><?= e($album['description']) ?></p>
        <?php endif; ?>
    </div>
</section>

<!-- Grille des photos -->
<section class="section section-album-photos">
    <div class="container">
        <?php if (empty($photos)): ?>
            <div class="empty-state" style="text-align:center;padding:4rem 0">
                <?= icon('image', 48, '', 'var(--vert-clair)') ?>
                <h2 style="margin-top:1rem">Aucune photo dans cet album</h2>
            </div>
        <?php else: ?>
            <p style="color:var(--brun);margin-bottom:1.5rem"><?= count($photos) ?> photo<?= count($photos) > 1 ? 's' : '' ?></p>

            <div class="photo-grid grid grid-4">
                <?php foreach ($photos as $index => $photo): ?>
                    <div class="photo-item card"
                         data-lightbox="album"
                         data-index="<?= $index ?>"
                         data-src="<?= e($baseUrl . '/storage/uploads/large/' . $photo['filename']) ?>"
                         data-title="<?= e($photo['title'] ?? '') ?>"
                         data-description="<?= e($photo['description'] ?? '') ?>"
                         style="cursor:pointer">
                        <?php if ($photo['image']): ?>
                            <?= img($photo['image'], $photo['title'] ?? $album['title'], 'photo-thumb') ?>
                        <?php else: ?>
                            <div style="background:var(--creme-fonce);height:180px;display:flex;align-items:center;justify-content:center">
                                <?= icon('image', 32, '', 'var(--vert-clair)') ?>
                            </div>
                        <?php endif; ?>
                        <?php if ($photo['title']): ?>
                            <div class="card-body" style="padding:.75rem">
                                <p style="font-size:.85rem;font-weight:500"><?= e($photo['title']) ?></p>
                            </div>
                        <?php endif; ?>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>

        <div style="margin-top:2rem">
            <a href="/galerie" class="btn btn-outline">
                <?= icon('arrow-left', 18) ?> Retour à la galerie
            </a>
        </div>
    </div>
</section>
