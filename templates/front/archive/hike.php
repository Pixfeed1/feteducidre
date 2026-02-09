<?php
/**
 * Template page randonnée.
 * Variables : $hikeEdition, $mapImage, $pastEditions, $seo
 */
?>

<!-- En-tête de page -->
<section class="page-header">
    <div class="container">
        <h1><?= icon('mountain', 32) ?> Randonnée</h1>
        <p>Parcourez les chemins du bocage angevin au coeur de la Fête du Cidre</p>
    </div>
</section>

<!-- Détail de l'édition courante -->
<?php if ($hikeEdition): ?>
<section class="section">
    <div class="container">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:3rem;align-items:start">

            <!-- Informations -->
            <div>
                <h2><?= e($hikeEdition['title'] ?? 'Randonnée ' . $hikeEdition['year']) ?></h2>

                <?php if ($hikeEdition['date']): ?>
                    <p style="margin-top:.75rem;display:flex;align-items:center;gap:.5rem;font-size:1.1rem">
                        <?= icon('calendar', 20, '', 'var(--orange-cidre)') ?>
                        <strong><?= date_fr($hikeEdition['date']) ?></strong>
                    </p>
                <?php endif; ?>

                <!-- Caractéristiques du parcours -->
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem;margin-top:1.5rem">
                    <?php if ($hikeEdition['distance_km']): ?>
                        <div class="card">
                            <div class="card-body" style="text-align:center;padding:1rem">
                                <?= icon('map', 24, '', 'var(--vert-mousse)') ?>
                                <span style="display:block;font-size:1.5rem;font-weight:700;margin-top:.25rem"><?= number_format((float) $hikeEdition['distance_km'], 1, ',', '') ?> km</span>
                                <span style="font-size:.85rem;color:var(--brun)">Distance</span>
                            </div>
                        </div>
                    <?php endif; ?>
                    <?php if ($hikeEdition['elevation_gain']): ?>
                        <div class="card">
                            <div class="card-body" style="text-align:center;padding:1rem">
                                <?= icon('mountain', 24, '', 'var(--vert-mousse)') ?>
                                <span style="display:block;font-size:1.5rem;font-weight:700;margin-top:.25rem"><?= (int) $hikeEdition['elevation_gain'] ?> m</span>
                                <span style="font-size:.85rem;color:var(--brun)">Dénivelé</span>
                            </div>
                        </div>
                    <?php endif; ?>
                    <?php if ($hikeEdition['participant_count']): ?>
                        <div class="card">
                            <div class="card-body" style="text-align:center;padding:1rem">
                                <?= icon('users', 24, '', 'var(--vert-mousse)') ?>
                                <span style="display:block;font-size:1.5rem;font-weight:700;margin-top:.25rem"><?= (int) $hikeEdition['participant_count'] ?></span>
                                <span style="font-size:.85rem;color:var(--brun)">Participants</span>
                            </div>
                        </div>
                    <?php endif; ?>
                </div>

                <?php if ($hikeEdition['description']): ?>
                    <div style="margin-top:1.5rem;line-height:1.8">
                        <?= sanitize($hikeEdition['description']) ?>
                    </div>
                <?php endif; ?>

                <div style="display:flex;gap:1rem;margin-top:1.5rem;flex-wrap:wrap">
                    <a href="/randonnee/classement" class="btn btn-primary">
                        <?= icon('award', 18) ?> Voir le classement
                    </a>
                    <?php if ($hikeEdition['gpx_file']): ?>
                        <a href="<?= e(\App\Core\Config::baseUrl() . '/storage/uploads/' . $hikeEdition['gpx_file']) ?>"
                           class="btn btn-outline" download>
                            <?= icon('download', 18) ?> Télécharger le GPX
                        </a>
                    <?php endif; ?>
                </div>
            </div>

            <!-- Carte du parcours -->
            <div>
                <?php if ($mapImage): ?>
                    <?= img($mapImage, 'Carte du parcours ' . $hikeEdition['year'], 'hike-map-img') ?>
                <?php else: ?>
                    <div style="background:var(--creme-fonce);height:350px;border-radius:14px;display:flex;align-items:center;justify-content:center">
                        <?= icon('map', 64, '', 'var(--vert-clair)') ?>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </div>
</section>
<?php endif; ?>

<!-- Éditions passées -->
<?php if (!empty($pastEditions) && count($pastEditions) > 1): ?>
<section class="section" style="background:var(--blanc)">
    <div class="container">
        <div class="section-title">
            <h2>Historique des randonnées</h2>
        </div>

        <div style="overflow-x:auto">
            <table style="width:100%;border-collapse:collapse;min-width:400px">
                <thead>
                    <tr style="border-bottom:2px solid var(--creme-fonce)">
                        <th style="text-align:left;padding:.75rem;font-weight:600">Année</th>
                        <th style="text-align:left;padding:.75rem;font-weight:600">Titre</th>
                        <th style="text-align:center;padding:.75rem;font-weight:600">Distance</th>
                        <th style="text-align:center;padding:.75rem;font-weight:600">Participants</th>
                        <th style="text-align:right;padding:.75rem;font-weight:600"></th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($pastEditions as $pastEdition): ?>
                        <tr style="border-bottom:1px solid var(--creme-fonce)">
                            <td style="padding:.75rem;font-weight:700"><?= (int) $pastEdition['year'] ?></td>
                            <td style="padding:.75rem"><?= e($pastEdition['title'] ?? 'Randonnée ' . $pastEdition['year']) ?></td>
                            <td style="text-align:center;padding:.75rem">
                                <?= $pastEdition['distance_km'] ? number_format((float) $pastEdition['distance_km'], 1, ',', '') . ' km' : '—' ?>
                            </td>
                            <td style="text-align:center;padding:.75rem">
                                <?= $pastEdition['participant_count'] ? (int) $pastEdition['participant_count'] : '—' ?>
                            </td>
                            <td style="text-align:right;padding:.75rem">
                                <a href="/randonnee/classement?year=<?= (int) $pastEdition['year'] ?>" class="btn-link" style="font-size:.9rem;font-weight:600;color:var(--orange-cidre)">
                                    Classement <?= icon('arrow-right', 14) ?>
                                </a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</section>
<?php endif; ?>
