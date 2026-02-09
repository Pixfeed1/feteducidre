<?php
/**
 * Footer du site.
 * Liens, réseaux sociaux, mentions légales.
 */
$baseUrl = \App\Core\Config::baseUrl();

// Récupérer les settings sociaux
try {
    $footerSettings = [];
    $rows = \App\Core\Database::getInstance()->fetchAll(
        "SELECT `group`, `key`, value FROM settings WHERE `group` IN ('general', 'social')"
    );
    foreach ($rows as $row) {
        $footerSettings[$row['group']][$row['key']] = $row['value'];
    }
} catch (\Exception) {
    $footerSettings = [];
}

$facebookUrl = $footerSettings['social']['facebook_url'] ?? '';
$instagramUrl = $footerSettings['social']['instagram_url'] ?? '';
$youtubeUrl = $footerSettings['social']['youtube_url'] ?? '';
$associationName = $footerSettings['general']['association_name'] ?? 'Association Fête du Cidre';
$associationAddress = $footerSettings['general']['association_address'] ?? 'L\'Hôtellerie de Flée, 49500';
$associationEmail = $footerSettings['general']['association_email'] ?? 'contact@fetecidre.fr';
?>
<footer class="site-footer">
    <div class="container">
        <div class="footer-grid">
            <!-- À propos -->
            <div class="footer-col">
                <h3 class="footer-title">Fête du Cidre</h3>
                <p class="footer-text">
                    Association loi 1901 — Depuis 1989, la Fête du Cidre célèbre le patrimoine cidricole
                    du Maine-et-Loire à L'Hôtellerie de Flée.
                </p>
                <div class="footer-social">
                    <?php if ($facebookUrl): ?>
                        <a href="<?= e($facebookUrl) ?>" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
                            <?= icon('facebook', 20) ?>
                        </a>
                    <?php endif; ?>
                    <?php if ($instagramUrl): ?>
                        <a href="<?= e($instagramUrl) ?>" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
                            <?= icon('instagram', 20) ?>
                        </a>
                    <?php endif; ?>
                    <?php if ($youtubeUrl): ?>
                        <a href="<?= e($youtubeUrl) ?>" target="_blank" rel="noopener noreferrer" aria-label="YouTube">
                            <?= icon('youtube', 20) ?>
                        </a>
                    <?php endif; ?>
                </div>
            </div>

            <!-- Navigation rapide -->
            <div class="footer-col">
                <h3 class="footer-title">Navigation</h3>
                <ul class="footer-links">
                    <li><a href="/">Accueil</a></li>
                    <li><a href="/origines">Nos Origines</a></li>
                    <li><a href="/infos-pratiques">Infos Pratiques</a></li>
                    <li><a href="/boutique">Boutique</a></li>
                    <li><a href="/galerie">Galerie</a></li>
                    <li><a href="/archives">Archives</a></li>
                </ul>
            </div>

            <!-- Contact -->
            <div class="footer-col">
                <h3 class="footer-title">Contact</h3>
                <ul class="footer-contact">
                    <li>
                        <?= icon('map-pin', 18) ?>
                        <span><?= e($associationAddress) ?></span>
                    </li>
                    <li>
                        <?= icon('mail', 18) ?>
                        <a href="mailto:<?= e($associationEmail) ?>"><?= e($associationEmail) ?></a>
                    </li>
                </ul>
            </div>
        </div>

        <div class="footer-bottom">
            <p>&copy; <?= date('Y') ?> <?= e($associationName) ?> — Tous droits réservés</p>
            <div class="footer-legal">
                <a href="/mentions-legales">Mentions légales</a>
                <a href="/contact">Contact</a>
            </div>
        </div>
    </div>
</footer>
