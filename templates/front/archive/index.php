<?php
/**
 * Template liste des éditions / archives.
 * Variables : $editions, $seo
 */
?>

<!-- En-tête de page -->
<section class="page-header">
    <div class="container">
        <h1><?= icon('calendar', 32) ?> Archives</h1>
        <p>Toutes les éditions de la Fête du Cidre depuis 1989</p>
    </div>
</section>

<!-- Grille des éditions -->
<section class="section section-archives">
    <div class="container">
        <?php if (empty($editions)): ?>
            <div class="empty-state" style="text-align:center;padding:4rem 0">
                <?= icon('calendar', 48, '', 'var(--vert-clair)') ?>
                <h2 style="margin-top:1rem">Aucune édition disponible</h2>
                <p>Les archives seront bientôt en ligne.</p>
            </div>
        <?php else: ?>
            <div class="grid grid-4">
                <?php foreach ($editions as $edition): ?>
                    <a href="/archives/<?= (int) $edition['year'] ?>" class="card edition-card" style="text-decoration:none;color:inherit">
                        <div class="card-body" style="text-align:center;padding:2rem">
                            <span class="edition-year" style="display:block;font-size:2.5rem;font-weight:900;color:var(--vert-profond);font-family:'Playfair Display',Georgia,serif;line-height:1"><?= (int) $edition['year'] ?></span>
                            <h3 style="margin-top:.75rem;font-size:1.1rem"><?= e($edition['title'] ?? 'Édition ' . $edition['year']) ?></h3>
                            <?php if ($edition['description']): ?>
                                <p style="margin-top:.5rem;font-size:.9rem;color:var(--brun)"><?= e(truncate($edition['description'], 100)) ?></p>
                            <?php endif; ?>
                            <span class="btn-link" style="display:inline-flex;align-items:center;gap:.25rem;margin-top:1rem;color:var(--orange-cidre);font-weight:600;font-size:.9rem">
                                Découvrir <?= icon('arrow-right', 16) ?>
                            </span>
                        </div>
                    </a>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </div>
</section>
