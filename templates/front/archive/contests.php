<?php
/**
 * Template page concours de cidre.
 * Variables : $years, $latestYear, $latestResults, $seo
 */
?>

<!-- En-tête de page -->
<section class="page-header">
    <div class="container">
        <h1><?= icon('trophy', 32) ?> Concours de Cidre</h1>
        <p>Le rendez-vous incontournable des producteurs de cidre du Maine-et-Loire</p>
    </div>
</section>

<!-- Présentation du concours -->
<section class="section">
    <div class="container">
        <div class="grid grid-2" style="gap:3rem;align-items:center">
            <div>
                <h2>Un concours d'exception</h2>
                <p style="margin-top:1rem;line-height:1.8">
                    Chaque année, le concours de la Fête du Cidre réunit les meilleurs producteurs de la région
                    pour une dégustation à l'aveugle. Un jury d'experts évalue les cidres selon des critères
                    rigoureux : robe, nez, bouche et équilibre.
                </p>
                <p style="margin-top:1rem;line-height:1.8">
                    Les médailles d'or, d'argent et de bronze récompensent les cidres d'exception qui font
                    la fierté de notre terroir.
                </p>
                <div style="display:flex;gap:1rem;margin-top:1.5rem;flex-wrap:wrap">
                    <a href="/concours/inscription" class="btn btn-secondary">
                        <?= icon('edit', 18) ?> S'inscrire au concours
                    </a>
                    <a href="/concours/palmares" class="btn btn-outline">
                        <?= icon('award', 18) ?> Voir le palmarès
                    </a>
                </div>
            </div>
            <div class="card" style="padding:0">
                <div style="background:var(--creme-fonce);height:300px;display:flex;align-items:center;justify-content:center;border-radius:14px">
                    <?= icon('trophy', 64, '', 'var(--vert-clair)') ?>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Derniers résultats -->
<?php if (!empty($latestResults)): ?>
<section class="section" style="background:var(--blanc)">
    <div class="container">
        <div class="section-title">
            <h2>Résultats <?= $latestYear ?></h2>
            <p>Les lauréats de la dernière édition du concours</p>
        </div>

        <?php
        // Grouper par catégorie
        $byCategory = [];
        foreach ($latestResults as $result) {
            $byCategory[$result['category']][] = $result;
        }
        ?>

        <div class="grid grid-2">
            <?php foreach ($byCategory as $category => $results): ?>
                <div class="card">
                    <div class="card-body" style="padding:1.5rem">
                        <h3 style="margin-bottom:1rem"><?= e($category) ?></h3>
                        <?php foreach (array_slice($results, 0, 3) as $result): ?>
                            <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.75rem;padding:.5rem 0;border-bottom:1px solid var(--creme-fonce)">
                                <?php if ($result['medal']): ?>
                                    <?= icon('award', 20, '', match($result['medal']) { 'or' => '#FFD700', 'argent' => '#C0C0C0', 'bronze' => '#CD7F32', default => 'var(--brun)' }) ?>
                                <?php else: ?>
                                    <span style="display:inline-block;width:20px;text-align:center;font-weight:700;color:var(--brun)"><?= (int) $result['rank'] ?></span>
                                <?php endif; ?>
                                <div style="flex:1">
                                    <strong><?= e($result['producer_name']) ?></strong>
                                    <?php if ($result['producer_city']): ?>
                                        <small style="color:var(--brun)"> — <?= e($result['producer_city']) ?></small>
                                    <?php endif; ?>
                                    <?php if ($result['product_name']): ?>
                                        <br><small style="color:var(--brun)"><?= e($result['product_name']) ?></small>
                                    <?php endif; ?>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>

        <div style="text-align:center;margin-top:2rem">
            <a href="/concours/palmares" class="btn btn-primary">
                Voir le palmarès complet <?= icon('arrow-right', 18) ?>
            </a>
        </div>
    </div>
</section>
<?php endif; ?>

<!-- Historique des années -->
<?php if (!empty($years)): ?>
<section class="section">
    <div class="container">
        <div class="section-title">
            <h2>Historique du concours</h2>
            <p>Consultez les résultats des éditions passées</p>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:.75rem;justify-content:center">
            <?php foreach ($years as $yearRow): ?>
                <a href="/concours/palmares?year=<?= (int) $yearRow['year'] ?>" class="btn btn-outline btn-sm">
                    <?= (int) $yearRow['year'] ?>
                </a>
            <?php endforeach; ?>
        </div>
    </div>
</section>
<?php endif; ?>
