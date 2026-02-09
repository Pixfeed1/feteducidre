<?php
/**
 * Footer du site — design premium.
 * Liens, réseaux sociaux, crédit Pixfeed.
 */
$baseUrl = \App\Core\Config::baseUrl();

// Récupérer les settings sociaux et généraux
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
$associationName = $footerSettings['general']['association_name'] ?? 'Association la Fête du Cidre';
$helloassoUrl = $footerSettings['general']['helloasso_url'] ?? 'https://www.helloasso.com/associations/cidre-du-haut-anjou';
?>
<footer class="site-footer">
    <div class="footer-inner">
        <div class="footer-brand">
            <div class="logo-text">Fête du Cidre <span>L'Hôtellerie de Flée</span></div>
            <p>Depuis plus de 35 ans, la Fête du Cidre célèbre le terroir et le savoir-faire du Haut Anjou dans une ambiance conviviale et festive.</p>
            <?php if ($facebookUrl || $instagramUrl || $youtubeUrl): ?>
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
            <?php endif; ?>
        </div>
        <div class="footer-col">
            <h4>Navigation</h4>
            <ul>
                <li><a href="/">Accueil</a></li>
                <li><a href="/concours">Concours</a></li>
                <li><a href="/archives">Archives</a></li>
                <li><a href="/infos-pratiques">Infos pratiques</a></li>
            </ul>
        </div>
        <div class="footer-col">
            <h4>Liens</h4>
            <ul>
                <li><a href="<?= e($helloassoUrl) ?>" target="_blank" rel="noopener">HelloAsso</a></li>
                <li><a href="/mentions-legales">Mentions légales</a></li>
                <li><a href="/contact">Nous contacter</a></li>
            </ul>
        </div>
    </div>
    <div class="footer-bottom">
        <span>&copy; <?= date('Y') ?> <?= e($associationName) ?>. Tous droits réservés.</span>
        <span>Développé par <a href="https://pixfeed.net" target="_blank" rel="noopener">Pixfeed</a></span>
    </div>
</footer>
