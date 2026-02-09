<?php
/**
 * Template palmarès du concours.
 * Variables : $years, $selectedYear, $grouped, $seo
 */
?>

<!-- En-tête de page -->
<section class="page-header">
    <div class="container">
        <h1><?= icon('award', 32) ?> Palmarès du Concours</h1>
        <p>Résultats et classements par année et catégorie</p>
    </div>
</section>

<section class="section">
    <div class="container">

        <!-- Sélecteur d'année -->
        <?php if (!empty($years)): ?>
            <div class="filter-bar" style="margin-bottom:2rem">
                <?php foreach ($years as $yearRow): ?>
                    <a href="/concours/palmares?year=<?= (int) $yearRow['year'] ?>"
                       class="btn <?= (int) $yearRow['year'] === $selectedYear ? 'btn-primary' : 'btn-outline' ?> btn-sm">
                        <?= (int) $yearRow['year'] ?>
                    </a>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>

        <?php if ($selectedYear): ?>
            <h2 style="margin-bottom:2rem">Résultats <?= $selectedYear ?></h2>
        <?php endif; ?>

        <?php if (empty($grouped)): ?>
            <div class="empty-state" style="text-align:center;padding:4rem 0">
                <?= icon('award', 48, '', 'var(--vert-clair)') ?>
                <h2 style="margin-top:1rem">Aucun résultat disponible</h2>
                <p>Les résultats pour cette année ne sont pas encore publiés.</p>
            </div>
        <?php else: ?>
            <?php foreach ($grouped as $category => $results): ?>
                <div class="card" style="margin-bottom:2rem">
                    <div class="card-body" style="padding:1.5rem">
                        <h3 style="margin-bottom:1rem"><?= icon('trophy', 20) ?> <?= e($category) ?></h3>

                        <div style="overflow-x:auto">
                            <table style="width:100%;border-collapse:collapse;min-width:500px">
                                <thead>
                                    <tr style="border-bottom:2px solid var(--creme-fonce)">
                                        <th style="text-align:left;padding:.5rem .75rem;font-weight:600;width:60px">Rang</th>
                                        <th style="text-align:left;padding:.5rem .75rem;font-weight:600">Producteur</th>
                                        <th style="text-align:left;padding:.5rem .75rem;font-weight:600">Ville</th>
                                        <th style="text-align:left;padding:.5rem .75rem;font-weight:600">Produit</th>
                                        <th style="text-align:center;padding:.5rem .75rem;font-weight:600;width:80px">Score</th>
                                        <th style="text-align:center;padding:.5rem .75rem;font-weight:600;width:100px">Médaille</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php foreach ($results as $result): ?>
                                        <tr style="border-bottom:1px solid var(--creme-fonce)">
                                            <td style="padding:.5rem .75rem;font-weight:700"><?= (int) $result['rank'] ?></td>
                                            <td style="padding:.5rem .75rem;font-weight:600"><?= e($result['producer_name']) ?></td>
                                            <td style="padding:.5rem .75rem;color:var(--brun)"><?= e($result['producer_city'] ?? '') ?></td>
                                            <td style="padding:.5rem .75rem"><?= e($result['product_name'] ?? '') ?></td>
                                            <td style="text-align:center;padding:.5rem .75rem">
                                                <?php if ($result['score'] !== null): ?>
                                                    <?= number_format((float) $result['score'], 2, ',', '') ?>
                                                <?php else: ?>
                                                    —
                                                <?php endif; ?>
                                            </td>
                                            <td style="text-align:center;padding:.5rem .75rem">
                                                <?php if ($result['medal']): ?>
                                                    <span style="display:inline-flex;align-items:center;gap:.25rem;font-weight:600;font-size:.85rem">
                                                        <?= icon('award', 16, '', match($result['medal']) { 'or' => '#FFD700', 'argent' => '#C0C0C0', 'bronze' => '#CD7F32', default => 'var(--brun)' }) ?>
                                                        <?= e(ucfirst($result['medal'])) ?>
                                                    </span>
                                                <?php else: ?>
                                                    —
                                                <?php endif; ?>
                                            </td>
                                        </tr>
                                    <?php endforeach; ?>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            <?php endforeach; ?>
        <?php endif; ?>

        <!-- Navigation -->
        <div style="margin-top:2rem">
            <a href="/concours" class="btn btn-outline">
                <?= icon('arrow-left', 18) ?> Retour au concours
            </a>
        </div>
    </div>
</section>
