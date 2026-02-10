<?php
/**
 * Template classement de la randonnée.
 * Variables : $years, $selectedYear, $results, $seo
 */
?>

<!-- Page Hero -->
<section class="page-hero">
    <div class="page-hero-pattern"></div>
    <div class="page-hero-decoration"></div>
    <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane">
            <a href="/">Accueil</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <a href="/randonnee">Randonnée</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <span aria-current="page">Classement</span>
        </nav>

        <span class="page-hero-badge">
            <?= icon('award', 16) ?> Classement
        </span>

        <h1 class="page-hero-title">Classement <em>Randonnée</em></h1>

        <p class="page-hero-intro">Résultats et temps des participants</p>
    </div>
</section>

<section class="section">
    <div class="container">

        <!-- Sélecteur d'année -->
        <?php if (!empty($years)): ?>
            <div class="filter-bar" style="margin-bottom:2rem">
                <?php foreach ($years as $yearRow): ?>
                    <a href="/randonnee/classement?year=<?= (int) $yearRow['year'] ?>"
                       class="btn <?= (int) $yearRow['year'] === $selectedYear ? 'btn-primary' : 'btn-outline' ?> btn-sm">
                        <?= (int) $yearRow['year'] ?>
                    </a>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>

        <?php if ($selectedYear): ?>
            <h2 style="margin-bottom:2rem">Classement <?= $selectedYear ?></h2>
        <?php endif; ?>

        <?php if (empty($results)): ?>
            <div class="empty-state" style="text-align:center;padding:4rem 0">
                <?= icon('award', 48, '', 'var(--vert-clair)') ?>
                <h2 style="margin-top:1rem">Aucun résultat disponible</h2>
                <p style="color:var(--brun)">Les classements pour cette année ne sont pas encore publiés.</p>
            </div>
        <?php else: ?>
            <div class="card">
                <div class="card-body" style="padding:1.5rem">
                    <p style="color:var(--brun);margin-bottom:1rem"><?= count($results) ?> participant<?= count($results) > 1 ? 's' : '' ?> classé<?= count($results) > 1 ? 's' : '' ?></p>

                    <div style="overflow-x:auto">
                        <table style="width:100%;border-collapse:collapse;min-width:500px">
                            <thead>
                                <tr style="border-bottom:2px solid var(--creme-fonce)">
                                    <th style="text-align:center;padding:.5rem .75rem;font-weight:600;width:60px">Rang</th>
                                    <th style="text-align:center;padding:.5rem .75rem;font-weight:600;width:70px">Dossard</th>
                                    <th style="text-align:left;padding:.5rem .75rem;font-weight:600">Participant</th>
                                    <th style="text-align:center;padding:.5rem .75rem;font-weight:600">Catégorie</th>
                                    <th style="text-align:center;padding:.5rem .75rem;font-weight:600;width:100px">Temps</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($results as $result): ?>
                                    <tr style="border-bottom:1px solid var(--creme-fonce)<?= (int) $result['rank'] <= 3 ? ';background:var(--creme)' : '' ?>">
                                        <td style="text-align:center;padding:.5rem .75rem">
                                            <?php if ((int) $result['rank'] === 1): ?>
                                                <?= icon('award', 20, '', '#FFD700') ?>
                                            <?php elseif ((int) $result['rank'] === 2): ?>
                                                <?= icon('award', 20, '', '#C0C0C0') ?>
                                            <?php elseif ((int) $result['rank'] === 3): ?>
                                                <?= icon('award', 20, '', '#CD7F32') ?>
                                            <?php else: ?>
                                                <span style="font-weight:700"><?= (int) $result['rank'] ?></span>
                                            <?php endif; ?>
                                        </td>
                                        <td style="text-align:center;padding:.5rem .75rem;color:var(--brun)">
                                            <?= $result['bib_number'] !== null ? (int) $result['bib_number'] : '—' ?>
                                        </td>
                                        <td style="padding:.5rem .75rem;font-weight:600"><?= e($result['participant_name']) ?></td>
                                        <td style="text-align:center;padding:.5rem .75rem;color:var(--brun)"><?= e($result['category'] ?? '—') ?></td>
                                        <td style="text-align:center;padding:.5rem .75rem;font-weight:600;font-family:monospace">
                                            <?= $result['time_seconds'] !== null ? format_duration((int) $result['time_seconds']) : '—' ?>
                                        </td>
                                    </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        <?php endif; ?>

        <!-- Navigation -->
        <div style="margin-top:2rem">
            <a href="/randonnee" class="btn btn-outline">
                <?= icon('arrow-left', 18) ?> Retour à la randonnée
            </a>
        </div>
    </div>
</section>
