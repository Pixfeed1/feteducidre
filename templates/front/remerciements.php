<?php
/**
 * Template Remerciements — partenaires & carte.
 * Variables : $partners (grouped by category), $settings, $seo
 */
$catConfig = [
    'media' => [
        'icon'  => 'radio',
        'label' => 'Médias',
        'class' => 'cat-media',
    ],
    'institutionnel' => [
        'icon'  => 'landmark',
        'label' => 'Institutions & collectivités',
        'class' => 'cat-institutionnel',
    ],
    'entreprise' => [
        'icon'  => 'briefcase',
        'label' => 'Services & entreprises',
        'class' => 'cat-entreprise',
    ],
    'associatif' => [
        'icon'  => 'apple',
        'label' => 'Partenaires locaux',
        'class' => 'cat-associatif',
    ],
    'autre' => [
        'icon'  => 'heart',
        'label' => 'Autres partenaires',
        'class' => 'cat-autre',
    ],
];

$mapLat = $settings['map_lat'] ?? '47.695';
$mapLng = $settings['map_lng'] ?? '-0.855';
$address = $settings['address'] ?? "L'Hôtellerie de Flée, 49500";
?>

<!-- Page Hero -->
<section class="page-hero" style="text-align:center">
    <div class="page-hero-pattern"></div>
    <div class="page-hero-decoration"></div>
    <div class="page-hero-content" style="position:relative;z-index:2;max-width:700px;margin:0 auto;padding:5rem 2rem 4rem">
        <nav class="breadcrumb" style="justify-content:center;margin-bottom:1.5rem" aria-label="Fil d'Ariane">
            <a href="/">Accueil</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <a href="/infos-pratiques">Infos pratiques</a>
            <span class="breadcrumb-sep"><?= icon('chevron-right', 14) ?></span>
            <span aria-current="page">Remerciements</span>
        </nav>

        <span class="page-hero-badge">
            <?= icon('heart', 14) ?> Merci à tous
        </span>

        <h1 class="page-hero-title" style="margin-left:auto;margin-right:auto"><em>Remerciements</em></h1>

        <p class="page-hero-intro" style="margin-left:auto;margin-right:auto">La Fête du Cidre n'existerait pas sans le soutien précieux de nos partenaires et la générosité de nos bénévoles.</p>
    </div>
</section>

<section class="thanks-section">

    <div class="thanks-intro">
        <p>Nous adressons nos plus sincères remerciements à l'ensemble des partenaires, institutions, entreprises et bénévoles qui contribuent chaque année au succès de la Fête du Cidre.</p>
    </div>

    <?php foreach ($catConfig as $catKey => $cfg):
        if (empty($partners[$catKey])) continue;
    ?>
        <div class="partner-section <?= $cfg['class'] ?>">
            <div class="partner-head">
                <div class="partner-head-icon">
                    <?= icon($cfg['icon'], 20) ?>
                </div>
                <h2><?= e($cfg['label']) ?></h2>
            </div>
            <div class="partners-grid">
                <?php foreach ($partners[$catKey] as $partner): ?>
                    <?php if ($partner['website']): ?>
                        <a href="<?= e($partner['website']) ?>" target="_blank" rel="noopener" class="partner-card">
                    <?php else: ?>
                        <div class="partner-card">
                    <?php endif; ?>
                        <div class="partner-dot"></div>
                        <div>
                            <div class="partner-name"><?= e($partner['name']) ?></div>
                            <?php if ($partner['description']): ?>
                                <div class="partner-detail"><?= e($partner['description']) ?></div>
                            <?php endif; ?>
                        </div>
                    <?php if ($partner['website']): ?>
                        </a>
                    <?php else: ?>
                        </div>
                    <?php endif; ?>
                <?php endforeach; ?>
            </div>
        </div>
    <?php endforeach; ?>

    <?php if (empty($partners)): ?>
        <div style="text-align:center;padding:4rem 0">
            <div style="margin-bottom:1rem"><?= icon('heart', 48, '', 'var(--vert-clair)') ?></div>
            <h2 style="margin-bottom:.5rem">Partenaires à venir</h2>
            <p style="color:var(--texte-leger)">La liste de nos partenaires sera bientôt disponible.</p>
        </div>
    <?php endif; ?>

    <!-- Map -->
    <div class="thanks-map">
        <div class="thanks-map-head">
            <div class="partner-head-icon">
                <?= icon('map-pin', 20) ?>
            </div>
            <h2>Nous trouver</h2>
        </div>
        <div class="thanks-map-card">
            <div id="thanksMap"></div>
            <div class="thanks-map-footer">
                <div class="thanks-map-footer-text">
                    <strong>Le Parc du Drugeot</strong> — <?= e($address) ?>
                </div>
                <a href="https://www.openstreetmap.org/?mlat=<?= $mapLat ?>&mlon=<?= $mapLng ?>#map=15/<?= $mapLat ?>/<?= $mapLng ?>" target="_blank" rel="noopener" class="thanks-map-btn">
                    <?= icon('navigation', 14) ?> Ouvrir dans OSM
                </a>
            </div>
        </div>
    </div>

</section>

<!-- Leaflet.js -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script>
(function() {
    var lat = <?= (float) $mapLat ?>;
    var lng = <?= (float) $mapLng ?>;
    var map = L.map('thanksMap', {
        scrollWheelZoom: false
    }).setView([lat, lng], 14);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    var markerIcon = L.divIcon({
        html: '<svg width="32" height="42" viewBox="0 0 32 42" fill="none">'
            + '<path d="M16 0C7.16 0 0 7.16 0 16c0 12 16 26 16 26s16-14 16-26C32 7.16 24.84 0 16 0z" fill="#2C4A2E"/>'
            + '<circle cx="16" cy="15" r="7" fill="#FAF5EC"/>'
            + '<circle cx="16" cy="15" r="4" fill="#D4833B"/>'
            + '</svg>',
        className: '',
        iconSize: [32, 42],
        iconAnchor: [16, 42],
        popupAnchor: [0, -42]
    });

    L.marker([lat, lng], { icon: markerIcon })
        .addTo(map)
        .bindPopup(
            '<strong>Fête du Cidre</strong><br><?= addslashes(e($address)) ?>',
            { className: 'custom-popup' }
        );
})();
</script>
