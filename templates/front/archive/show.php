<?php
/**
 * Template détail d'une édition.
 * Variables : $edition, $poster, $contestResults, $seo
 */
?>

<!-- Fil d'Ariane -->
<section class="breadcrumb-section">
    <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane">
            <a href="/">Accueil</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <a href="/archives">Archives</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <span aria-current="page">Édition <?= (int) $edition['year'] ?></span>
        </nav>
    </div>
</section>

<!-- En-tête édition -->
<section class="page-header">
    <div class="container">
        <span style="font-size:1rem;color:var(--orange-cidre);font-weight:600"><?= icon('calendar', 18) ?> Édition</span>
        <h1><?= e($edition['title'] ?? 'Fête du Cidre ' . $edition['year']) ?></h1>
        <p style="font-size:1.5rem;font-weight:300"><?= (int) $edition['year'] ?></p>
    </div>
</section>

<!-- Contenu de l'édition -->
<section class="section">
    <div class="container">
        <div style="display:grid;grid-template-columns:<?= $poster ? '350px 1fr' : '1fr' ?>;gap:3rem;align-items:start">

            <!-- Affiche -->
            <?php if ($poster): ?>
                <div class="edition-poster">
                    <?= img($poster, 'Affiche ' . $edition['year'], 'edition-poster-img') ?>
                </div>
            <?php endif; ?>

            <!-- Description et détails -->
            <div class="edition-content">
                <?php if ($edition['description']): ?>
                    <div class="edition-description" style="line-height:1.8;margin-bottom:2rem">
                        <?= sanitize($edition['description']) ?>
                    </div>
                <?php endif; ?>

                <!-- Statistiques -->
                <?php if (!empty($edition['stats'])): ?>
                    <div class="edition-stats" style="display:flex;gap:1.5rem;flex-wrap:wrap;margin-bottom:2rem">
                        <?php foreach ($edition['stats'] as $stat): ?>
                            <div class="stat-item card" style="flex:1;min-width:150px">
                                <div class="card-body" style="text-align:center;padding:1.25rem">
                                    <span style="display:block;font-size:2rem;font-weight:900;color:var(--orange-cidre)"><?= e($stat['value'] ?? '') ?></span>
                                    <span style="font-size:.85rem;color:var(--brun)"><?= e($stat['label'] ?? '') ?></span>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>

                <!-- Temps forts -->
                <?php if (!empty($edition['highlights'])): ?>
                    <h2 style="margin-bottom:1rem"><?= icon('star', 22) ?> Temps forts</h2>
                    <div class="edition-highlights" style="margin-bottom:2rem">
                        <?php foreach ($edition['highlights'] as $highlight): ?>
                            <div style="display:flex;align-items:start;gap:.75rem;margin-bottom:1rem;padding:1rem;background:var(--blanc);border-radius:10px">
                                <?= icon('check-circle', 20, '', 'var(--vert-mousse)') ?>
                                <p><?= e($highlight) ?></p>
                            </div>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </div>
        </div>

        <!-- Résultats du concours pour cette année -->
        <?php if (!empty($contestResults)): ?>
            <div style="margin-top:3rem">
                <h2 style="margin-bottom:1.5rem"><?= icon('trophy', 22) ?> Résultats du concours <?= (int) $edition['year'] ?></h2>

                <?php
                // Grouper par catégorie
                $resultsByCategory = [];
                foreach ($contestResults as $result) {
                    $resultsByCategory[$result['category']][] = $result;
                }
                ?>

                <?php foreach ($resultsByCategory as $category => $results): ?>
                    <div class="card" style="margin-bottom:1.5rem">
                        <div class="card-body" style="padding:1.5rem">
                            <h3 style="margin-bottom:1rem"><?= e($category) ?></h3>
                            <table style="width:100%;border-collapse:collapse">
                                <thead>
                                    <tr style="border-bottom:2px solid var(--creme-fonce)">
                                        <th style="text-align:left;padding:.5rem 0;font-weight:600;width:60px">Rang</th>
                                        <th style="text-align:left;padding:.5rem 0;font-weight:600">Producteur</th>
                                        <th style="text-align:left;padding:.5rem 0;font-weight:600">Produit</th>
                                        <th style="text-align:center;padding:.5rem 0;font-weight:600;width:100px">Médaille</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php foreach ($results as $result): ?>
                                        <tr style="border-bottom:1px solid var(--creme-fonce)">
                                            <td style="padding:.5rem 0;font-weight:600"><?= (int) $result['rank'] ?></td>
                                            <td style="padding:.5rem 0">
                                                <?= e($result['producer_name']) ?>
                                                <?php if ($result['producer_city']): ?>
                                                    <small style="color:var(--brun)"> — <?= e($result['producer_city']) ?></small>
                                                <?php endif; ?>
                                            </td>
                                            <td style="padding:.5rem 0"><?= e($result['product_name'] ?? '') ?></td>
                                            <td style="text-align:center;padding:.5rem 0">
                                                <?php if ($result['medal']): ?>
                                                    <span class="medal medal-<?= e($result['medal']) ?>" style="display:inline-flex;align-items:center;gap:.25rem;font-weight:600;font-size:.85rem">
                                                        <?= icon('award', 16) ?> <?= e(ucfirst($result['medal'])) ?>
                                                    </span>
                                                <?php endif; ?>
                                            </td>
                                        </tr>
                                    <?php endforeach; ?>
                                </tbody>
                            </table>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>

        <!-- Navigation -->
        <div style="margin-top:2rem">
            <a href="/archives" class="btn btn-outline">
                <?= icon('arrow-left', 18) ?> Toutes les archives
            </a>
        </div>
    </div>
</section>
