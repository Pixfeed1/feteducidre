<?php
/**
 * Template page d'accueil — design premium.
 * Variables : $page, $seo, $settings, $featuredProducts, $editions, $partners, $currentEdition
 */

$eventDate = $settings['general']['next_event_date'] ?? '';
$eventLocation = $settings['general']['event_location'] ?? 'Parc du Drugeot';
$helloassoUrl = $settings['general']['helloasso_url'] ?? 'https://www.helloasso.com/associations/cidre-du-haut-anjou';
$editionYear = $currentEdition['year'] ?? date('Y');
$editionTitle = $currentEdition['title'] ?? '';
$heroDescription = $page['content'] ?? 'Une journée festive dédiée au terroir du Haut Anjou : circuit de 7 km, jeux d\'adresse, déjeuner aux saveurs locales, spectacle vivant et marché de producteurs.';
// Strip tags from page content if it contains HTML
$heroDescription = strip_tags($heroDescription);
if (strlen($heroDescription) > 250) {
    $heroDescription = mb_substr($heroDescription, 0, 250) . '…';
}
?>

<!-- HERO -->
<section class="hero">
    <div class="hero-bg-pattern"></div>
    <div class="hero-decoration"></div>
    <div class="hero-inner">
        <div class="hero-content">
            <div class="hero-badge">
                <span class="dot"></span>
                Édition <?= e((string)$editionYear) ?>
            </div>
            <h1 class="hero-title">La <em>Fête</em><br>du Cidre</h1>
            <?php if ($eventDate): ?>
                <p class="hero-date">Dimanche <strong><?= date_fr($eventDate) ?></strong></p>
            <?php endif; ?>
            <p class="hero-desc"><?= e($heroDescription) ?></p>
            <div class="hero-actions">
                <?php if ($helloassoUrl): ?>
                <a href="<?= e($helloassoUrl) ?>" class="btn btn-primary" target="_blank" rel="noopener">
                    Réserver le déjeuner
                    <?= icon('arrow-right', 18, '', 'currentColor', 2.5) ?>
                </a>
                <?php endif; ?>
                <a href="#programme" class="btn btn-outline">Découvrir le programme</a>
            </div>
        </div>

        <div class="hero-visual">
            <div class="hero-image-frame">
                <?php if (!empty($page['hero_image'])): ?>
                    <img src="<?= e($page['hero_image']) ?>" alt="Fête du Cidre — <?= e((string)$editionYear) ?>" loading="eager">
                <?php else: ?>
                    <div class="hero-image-placeholder">
                        <div class="apple-icon"><?= icon('apple', 80, '', 'white', 1.5) ?></div>
                        <p>Fête du Cidre</p>
                        <small><?= $eventDate ? date_fr($eventDate, 'day') : e((string)$editionYear) ?> — L'Hôtellerie de Flée</small>
                    </div>
                <?php endif; ?>
            </div>
            <div class="floating-card card-date">
                <div class="card-icon"><?= icon('calendar-days', 22, '', 'white', 2) ?></div>
                <div class="card-info">
                    <?php if ($eventDate): ?>
                        <strong><?= date_fr($eventDate, 'day') ?></strong>
                    <?php else: ?>
                        <strong><?= e((string)$editionYear) ?></strong>
                    <?php endif; ?>
                    Dimanche, toute la journée
                </div>
            </div>
            <div class="floating-card card-lieu">
                <div class="card-icon"><?= icon('map-pin', 22, '', 'white', 2) ?></div>
                <div class="card-info">
                    <strong><?= e($eventLocation) ?></strong>
                    L'Hôtellerie de Flée
                </div>
            </div>
        </div>
    </div>
</section>

<!-- PROGRAMME -->
<section class="section programme-section" id="programme">
    <div class="section-header reveal">
        <span class="section-label">Au programme</span>
        <h2 class="section-title">Une journée riche en découvertes</h2>
        <p class="section-subtitle">Retrouvez toutes les animations et activités qui font de la Fête du Cidre un rendez-vous incontournable du Haut Anjou.</p>
    </div>
    <div class="programme-grid">
        <div class="programme-card reveal">
            <div class="programme-icon"><?= icon('footprints', 26, '', 'var(--creme)', 2) ?></div>
            <h3>Rallye 7 km</h3>
            <p>Un circuit champêtre à travers le bocage, ponctué de jeux d'adresse et d'épreuves conviviales pour toute la famille.</p>
        </div>
        <div class="programme-card reveal">
            <div class="programme-icon"><?= icon('utensils', 26, '', 'var(--creme)', 2) ?></div>
            <h3>Déjeuner terroir</h3>
            <p>Pause gourmande mettant à l'honneur les plats locaux cuisinés au cidre. Réservation recommandée.</p>
        </div>
        <div class="programme-card reveal">
            <div class="programme-icon"><?= icon('drama', 26, '', 'var(--creme)', 2) ?></div>
            <h3>Spectacle vivant</h3>
            <p>Animation et divertissement pour petits et grands, dans l'ambiance chaleureuse du Parc du Drugeot.</p>
        </div>
        <div class="programme-card reveal">
            <div class="programme-icon"><?= icon('shopping-basket', 26, '', 'var(--creme)', 2) ?></div>
            <h3>Marché producteurs</h3>
            <p>Découvrez les produits du terroir angevin : cidres, jus, confitures et spécialités artisanales locales.</p>
        </div>
    </div>
</section>

<!-- CTA RÉSERVATION -->
<section class="section cta-section" id="reserver">
    <div class="cta-inner reveal">
        <span class="section-label">Ne manquez pas</span>
        <h2 class="section-title">Réservez votre déjeuner</h2>
        <p class="section-subtitle">Places limitées pour le repas du midi. Réservez dès maintenant via HelloAsso pour vous garantir un moment gourmand au cœur de la fête.</p>
        <?php if ($helloassoUrl): ?>
        <a href="<?= e($helloassoUrl) ?>" class="btn btn-cta" target="_blank" rel="noopener">
            Réserver sur HelloAsso
            <?= icon('arrow-right', 18, '', 'currentColor', 2.5) ?>
        </a>
        <?php endif; ?>
    </div>
</section>

<!-- CONCOURS -->
<section class="section concours-section" id="concours">
    <div class="section-header reveal">
        <span class="section-label">Participez</span>
        <h2 class="section-title">Concours du Cidre <?= e((string)$editionYear) ?></h2>
        <p class="section-subtitle">Professionnels, amateurs ou producteurs : inscrivez-vous au concours et faites déguster vos meilleures cuvées !</p>
    </div>
    <div class="concours-grid">
        <div class="concours-card reveal">
            <div class="card-emoji"><?= icon('trophy', 40, '', 'var(--orange-cidre)', 1.8) ?></div>
            <h3>Professionnels</h3>
            <p>Concours réservé aux cidriers professionnels du Grand Ouest.</p>
            <a href="/concours" class="btn-sm">Règlement & inscription <?= icon('arrow-right', 14) ?></a>
        </div>
        <div class="concours-card reveal">
            <div class="card-emoji"><?= icon('apple', 40, '', 'var(--vert-mousse)', 1.8) ?></div>
            <h3>Amateurs</h3>
            <p>Vous faites votre cidre maison ? Tentez votre chance au concours amateur.</p>
            <a href="/concours" class="btn-sm">Règlement & inscription <?= icon('arrow-right', 14) ?></a>
        </div>
        <div class="concours-card reveal">
            <div class="card-emoji"><?= icon('tree-deciduous', 40, '', 'var(--vert-profond)', 1.8) ?></div>
            <h3>Producteurs</h3>
            <p>Informations et inscriptions pour les producteurs locaux souhaitant participer.</p>
            <a href="/concours" class="btn-sm">Courrier producteurs <?= icon('arrow-right', 14) ?></a>
        </div>
    </div>
</section>

<!-- ARCHIVES -->
<section class="section archives-section" id="archives">
    <div class="section-header reveal">
        <span class="section-label">Souvenirs</span>
        <h2 class="section-title">Revivez les éditions passées</h2>
        <p class="section-subtitle">Photos, affiches, programmes et palmarès des concours depuis les origines de la fête.</p>
    </div>
    <div class="archives-grid reveal">
        <a href="/galerie" class="archives-item">
            <div class="archives-item-inner">
                <div class="archives-emoji"><?= icon('camera', 36, '', 'white', 1.8) ?></div>
                <span class="archives-label">Galerie</span>
                <span class="archives-title">Photos</span>
            </div>
        </a>
        <a href="/archives" class="archives-item">
            <div class="archives-item-inner">
                <div class="archives-emoji"><?= icon('image', 36, '', 'white', 1.8) ?></div>
                <span class="archives-label">Collection</span>
                <span class="archives-title">Affiches</span>
            </div>
        </a>
        <a href="/archives" class="archives-item">
            <div class="archives-item-inner">
                <div class="archives-emoji"><?= icon('clipboard-list', 36, '', 'white', 1.8) ?></div>
                <span class="archives-label">Historique</span>
                <span class="archives-title">Programmes</span>
            </div>
        </a>
        <a href="/concours/palmares" class="archives-item">
            <div class="archives-item-inner">
                <div class="archives-emoji"><?= icon('award', 36, '', 'white', 1.8) ?></div>
                <span class="archives-label">Palmarès</span>
                <span class="archives-title">Concours</span>
            </div>
        </a>
        <a href="/origines" class="archives-item">
            <div class="archives-item-inner">
                <div class="archives-emoji"><?= icon('book-open', 36, '', 'white', 1.8) ?></div>
                <span class="archives-label">Depuis 1987</span>
                <span class="archives-title">Origines</span>
            </div>
        </a>
    </div>
</section>

<!-- INFOS PRATIQUES -->
<section class="section infos-section" id="infos">
    <div class="section-header reveal">
        <span class="section-label">Pratique</span>
        <h2 class="section-title">Informations utiles</h2>
    </div>
    <div class="infos-grid">
        <div class="info-card reveal">
            <h3><span class="info-icon"><?= icon('map-pin', 20, '', 'var(--creme)', 2) ?></span> Accès & lieu</h3>
            <ul class="info-list">
                <li><span class="bullet"></span><?= e($eventLocation) ?>, L'Hôtellerie de Flée, 49500</li>
                <li><span class="bullet"></span>Accès libre et gratuit toute la journée</li>
                <li><span class="bullet"></span>Parking sur place</li>
                <li><span class="bullet"></span>Restauration sur réservation via <a href="<?= e($helloassoUrl) ?>" target="_blank" rel="noopener">HelloAsso</a></li>
            </ul>
        </div>
        <div class="info-card reveal">
            <h3><span class="info-icon"><?= icon('phone', 20, '', 'var(--creme)', 2) ?></span> Contact</h3>
            <ul class="info-list">
                <li><span class="bullet"></span>Association la Fête du Cidre</li>
                <li><span class="bullet"></span>Téléphone : <a href="tel:0679968754">06.79.96.87.54</a></li>
                <li><span class="bullet"></span>Email : <a href="mailto:contact@feteducidre.fr">contact@feteducidre.fr</a></li>
                <li><span class="bullet"></span>Suivez-nous sur <a href="<?= e($helloassoUrl) ?>" target="_blank" rel="noopener">HelloAsso</a> pour les actualités</li>
            </ul>
        </div>
    </div>
</section>
