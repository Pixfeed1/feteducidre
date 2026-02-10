<?php
/**
 * Template liste des éditions / archives.
 * Design premium avec page-hero + grille d'éditions.
 * Variables : $editions, $seo
 */
?>

<!-- Page Hero -->
<section class="page-hero">
    <div class="page-hero-pattern"></div>
    <div class="page-hero-decoration"></div>
    <div class="container">
        <span class="page-hero-badge">
            <?= icon('history', 16) ?> Nos Archives
        </span>

        <h1 class="page-hero-title">Toutes les <em>éditions</em></h1>

        <p class="page-hero-intro">Depuis 1989, la Fête du Cidre célèbre chaque année le terroir et le savoir-faire du Haut Anjou. Revivez les moments forts de chaque édition.</p>
    </div>
</section>

<!-- Grille des éditions -->
<section class="section">
    <div class="container">
        <?php if (empty($editions)): ?>
            <div class="empty-state" style="text-align:center;padding:4rem 0">
                <?= icon('calendar', 48, '', 'var(--vert-clair)') ?>
                <h2 style="margin-top:1rem">Aucune édition disponible</h2>
                <p style="color:var(--brun)">Les archives seront bientôt en ligne.</p>
            </div>
        <?php else: ?>
            <div class="grid grid-4">
                <?php foreach ($editions as $edition): ?>
                    <a href="/archives/<?= (int) $edition['year'] ?>" class="card edition-card reveal">
                        <div class="card-body" style="text-align:center;padding:2rem">
                            <span class="edition-year"><?= (int) $edition['year'] ?></span>
                            <h3 style="margin-top:.75rem;font-size:1.1rem"><?= e($edition['title'] ?? 'Édition ' . $edition['year']) ?></h3>
                            <?php if ($edition['description']): ?>
                                <p style="margin-top:.5rem;font-size:.9rem;color:var(--brun)"><?= e(truncate($edition['description'], 100)) ?></p>
                            <?php endif; ?>
                            <span class="btn-sm" style="margin-top:1rem">
                                Découvrir <?= icon('arrow-right', 14) ?>
                            </span>
                        </div>
                    </a>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </div>
</section>
