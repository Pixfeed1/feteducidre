<?php
/**
 * Template liste des albums de la galerie.
 * Variables : $albums, $seo
 */
?>

<!-- En-tête de page -->
<section class="page-header">
    <div class="container">
        <h1><?= icon('images', 32) ?> Galerie</h1>
        <p>Les plus beaux moments de la Fête du Cidre en images</p>
    </div>
</section>

<!-- Grille des albums -->
<section class="section section-gallery">
    <div class="container">
        <?php if (empty($albums)): ?>
            <div class="empty-state" style="text-align:center;padding:4rem 0">
                <?= icon('images', 48, '', 'var(--vert-clair)') ?>
                <h2 style="margin-top:1rem">Aucun album disponible</h2>
                <p>Les photos seront bientôt en ligne. Revenez nous voir !</p>
            </div>
        <?php else: ?>
            <div class="grid grid-3">
                <?php foreach ($albums as $album): ?>
                    <a href="/galerie/<?= e($album['slug']) ?>" class="card album-card" style="text-decoration:none;color:inherit">
                        <!-- Image de couverture -->
                        <div class="album-cover" style="position:relative;overflow:hidden">
                            <?php if ($album['cover_image']): ?>
                                <?= img($album['cover_image'], $album['title'], 'album-cover-img') ?>
                            <?php else: ?>
                                <div style="background:var(--creme-fonce);height:220px;display:flex;align-items:center;justify-content:center">
                                    <?= icon('image', 48, '', 'var(--vert-clair)') ?>
                                </div>
                            <?php endif; ?>

                            <!-- Badge nombre de photos -->
                            <?php if ($album['photo_count'] > 0): ?>
                                <span class="album-badge" style="position:absolute;bottom:.75rem;right:.75rem;background:rgba(0,0,0,.6);color:#fff;padding:.25rem .75rem;border-radius:20px;font-size:.85rem;font-weight:600">
                                    <?= icon('image', 14) ?> <?= (int) $album['photo_count'] ?>
                                </span>
                            <?php endif; ?>
                        </div>

                        <!-- Informations album -->
                        <div class="card-body">
                            <h3 style="margin-bottom:.25rem"><?= e($album['title']) ?></h3>
                            <?php if ($album['year']): ?>
                                <span style="color:var(--brun);font-size:.9rem"><?= icon('calendar', 14) ?> <?= (int) $album['year'] ?></span>
                            <?php endif; ?>
                            <?php if ($album['description']): ?>
                                <p style="margin-top:.5rem;color:var(--brun);font-size:.9rem"><?= e(truncate($album['description'], 120)) ?></p>
                            <?php endif; ?>
                            <span class="btn-link" style="display:inline-flex;align-items:center;gap:.25rem;margin-top:.75rem;color:var(--orange-cidre);font-weight:600;font-size:.9rem">
                                Voir l'album <?= icon('arrow-right', 16) ?>
                            </span>
                        </div>
                    </a>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </div>
</section>
