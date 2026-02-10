<?php
/**
 * Template page Infos Pratiques.
 * Variables : $page, $seo, $settings
 */
$siteName = $settings['general']['association_name'] ?? 'Association la Fête du Cidre';
$address  = $settings['general']['association_address'] ?? 'Le Parc du Drugeot, 49500 L\'Hôtellerie de Flée';
$email    = $settings['general']['association_email'] ?? 'contact@fetecidre.fr';
$phone    = $settings['general']['association_phone'] ?? '06.79.96.87.54';

$eventDate   = $settings['general']['next_event_date'] ?? 'Dimanche 14 Juin 2026';
$eventHours  = $settings['general']['next_event_time'] ?? '10h – 19h';
$eventEntry  = $settings['general']['next_event_price'] ?? 'Gratuite';

$mapLat = (float) ($settings['general']['map_latitude'] ?? 47.695);
$mapLng = (float) ($settings['general']['map_longitude'] ?? -0.855);
?>

<!-- Page Hero (centré) -->
<section class="page-hero" style="text-align:center">
    <div class="page-hero-pattern"></div>
    <div class="page-hero-decoration"></div>
    <div class="container">
        <span class="page-hero-badge">
            <?= icon('info', 16) ?> Infos pratiques
        </span>

        <h1 class="page-hero-title" style="margin-left:auto;margin-right:auto">Infos <em>Pratiques</em></h1>

        <p class="page-hero-intro" style="margin-left:auto;margin-right:auto">Tout ce qu'il faut savoir pour profiter de la Fête du Cidre</p>
    </div>
</section>

<!-- Quick Cards -->
<section class="section" style="padding-top:0;margin-top:-2rem;position:relative;z-index:3">
    <div class="container">
        <div class="quick-cards">
            <div class="quick-card">
                <div class="quick-card-icon" style="background:var(--orange-cidre)">
                    <?= icon('calendar', 24) ?>
                </div>
                <div>
                    <span class="quick-card-label">Date</span>
                    <strong class="quick-card-value"><?= e($eventDate) ?></strong>
                </div>
            </div>
            <div class="quick-card">
                <div class="quick-card-icon" style="background:var(--vert-mousse)">
                    <?= icon('ticket', 24) ?>
                </div>
                <div>
                    <span class="quick-card-label">Entrée</span>
                    <strong class="quick-card-value"><?= e($eventEntry) ?></strong>
                </div>
            </div>
            <div class="quick-card">
                <div class="quick-card-icon" style="background:var(--vert-profond)">
                    <?= icon('clock', 24) ?>
                </div>
                <div>
                    <span class="quick-card-label">Horaires</span>
                    <strong class="quick-card-value"><?= e($eventHours) ?></strong>
                </div>
            </div>
        </div>
    </div>
</section>

<?php if (!empty($page['content'])): ?>
<!-- Contenu éditorial CMS -->
<section class="section" style="padding-bottom:0">
    <div class="container cms-content">
        <?= sanitize($page['content']) ?>
    </div>
</section>
<?php endif; ?>

<!-- Contact + Accès -->
<section class="section">
    <div class="container">
        <div class="two-cols">

            <!-- Bloc Contact -->
            <div class="info-block">
                <div class="info-block-header">
                    <?= icon('building-2', 22, '', 'var(--vert-mousse)') ?>
                    Nous contacter
                </div>
                <div class="contact-list">
                    <div class="contact-item">
                        <span class="contact-dot"></span>
                        <div>
                            <strong>Association</strong>
                            <p><?= e($siteName) ?></p>
                        </div>
                    </div>
                    <div class="contact-item">
                        <span class="contact-dot"></span>
                        <div>
                            <strong>Adresse</strong>
                            <p><?= e($address) ?></p>
                        </div>
                    </div>
                    <?php if ($phone): ?>
                        <div class="contact-item">
                            <span class="contact-dot"></span>
                            <div>
                                <strong>Téléphone</strong>
                                <p><a href="tel:<?= e(phone_clean($phone)) ?>"><?= e($phone) ?></a></p>
                            </div>
                        </div>
                    <?php endif; ?>
                    <div class="contact-item">
                        <span class="contact-dot"></span>
                        <div>
                            <strong>Email</strong>
                            <p><a href="mailto:<?= e($email) ?>"><?= e($email) ?></a></p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Bloc Accès -->
            <div class="info-block">
                <div class="info-block-header">
                    <?= icon('route', 22, '', 'var(--vert-mousse)') ?>
                    Venir &amp; Accès
                </div>
                <div class="access-list">
                    <div class="access-item">
                        <?= icon('car', 20) ?>
                        <div><strong>En voiture :</strong> Depuis Angers, prendre la direction de Château-Gontier (D770). Fléchage à partir du bourg de Flée.</div>
                    </div>
                    <div class="access-item">
                        <?= icon('circle-parking', 20) ?>
                        <div><strong>Stationnement :</strong> Parking gratuit à proximité du site. Suivre les indications des bénévoles.</div>
                    </div>
                    <div class="access-item">
                        <?= icon('utensils', 20) ?>
                        <div><strong>Restauration :</strong> Buvette et restauration sur place tout au long de la journée.</div>
                    </div>
                    <div class="access-item">
                        <?= icon('accessibility', 20) ?>
                        <div><strong>Accessibilité :</strong> Le site est accessible aux personnes à mobilité réduite. Contactez-nous pour toute demande spécifique.</div>
                    </div>
                </div>
            </div>

        </div>
    </div>
</section>

<!-- Carte interactive -->
<section class="section" style="padding-top:0">
    <div class="container">
        <div class="map-card">
            <div id="infos-map"></div>
            <div class="map-overlay">
                <div class="map-overlay-address">
                    <?= icon('map-pin', 20, '', 'var(--orange-cidre)') ?>
                    <span><?= e($address) ?></span>
                </div>
                <a href="https://www.google.com/maps/dir/?api=1&destination=<?= $mapLat ?>,<?= $mapLng ?>"
                   target="_blank" rel="noopener noreferrer"
                   class="btn btn-primary btn-sm">
                    <?= icon('navigation', 16) ?> Itinéraire
                </a>
            </div>
        </div>
    </div>
</section>

<!-- CTA Remerciements -->
<section class="section" style="padding-top:0">
    <div class="container" style="max-width:700px">
        <a href="/remerciements" class="cta-card">
            <?= icon('heart', 32, '', 'var(--orange-doux)') ?>
            <h3>Ils font la fête avec nous</h3>
            <p>Découvrez nos partenaires et bénévoles qui rendent cet événement possible</p>
            <span class="cta-arrow"><?= icon('arrow-right', 20) ?></span>
        </a>
    </div>
</section>

<!-- Leaflet.js -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script>
(function() {
    var lat = <?= $mapLat ?>;
    var lng = <?= $mapLng ?>;
    var map = L.map('infos-map', {
        scrollWheelZoom: false
    }).setView([lat, lng], 14);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    var markerIcon = L.divIcon({
        html: '<svg width="32" height="42" viewBox="0 0 32 42" fill="none" xmlns="http://www.w3.org/2000/svg">'
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
            '<strong>Fête du Cidre</strong>' +
            '<?= addslashes(e($address)) ?>',
            { className: 'custom-popup' }
        );
})();
</script>
