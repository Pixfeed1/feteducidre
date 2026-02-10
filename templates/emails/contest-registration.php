<?php
$_baseUrl = \App\Core\Config::baseUrl();
$_producer = e($producer ?? '');
$_contactName = e($contact_name ?? $contact ?? '');
$_contactEmail = e($contact_email ?? '');
$_contactPhone = e($contact_phone ?? '');
$_contactAddress = e($contact_address ?? '');
$_totalProducts = is_array($products ?? null) ? count($products) : 0;

// Stats
$_statsRegistered = (int)($stats_registered ?? $stats['registered'] ?? 0);
$_statsProducts = (int)($stats_products ?? $stats['products'] ?? 0);
$_statsWeek = (int)($stats_week ?? $stats['this_week'] ?? 0);

// Category color mapping
$_categoryColors = [
    'brut' => ['bg' => 'rgba(212,131,59,0.1)', 'color' => '#D4833B'],
    'demi-sec' => ['bg' => 'rgba(122,158,107,0.1)', 'color' => '#4A6B3E'],
    'doux' => ['bg' => 'rgba(139,92,246,0.1)', 'color' => '#8B5CF6'],
    'jus' => ['bg' => 'rgba(59,130,246,0.1)', 'color' => '#3B82F6'],
    'pommeau' => ['bg' => 'rgba(236,72,153,0.1)', 'color' => '#EC4899'],
];
?>
<!-- Compact admin header -->
<div style="background:#2C4A2E;padding:1.2rem 2rem">
    <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
        <td width="36" style="vertical-align:middle">
            <div style="width:36px;height:36px;background:#4A6B3E;border-radius:10px;line-height:36px;text-align:center">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" style="vertical-align:middle"><circle cx="12" cy="14" r="8" fill="#7A9E6B"/><ellipse cx="12" cy="13" rx="5" ry="7" fill="#A3C48E"/></svg>
            </div>
        </td>
        <td style="padding-left:12px;vertical-align:middle">
            <div style="font-family:Georgia,serif;font-size:1rem;font-weight:900;color:#FAF5EC">Fête du Cidre</div>
            <div style="font-size:0.65rem;color:rgba(250,245,236,0.4);letter-spacing:0.1em;text-transform:uppercase">Notification admin</div>
        </td>
        <td style="text-align:right;vertical-align:middle">
            <span style="background:#7A9E6B;color:white;padding:0.3rem 0.8rem;border-radius:100px;font-size:0.72rem;font-weight:700">CONCOURS</span>
        </td>
    </tr></table>
</div>

<!-- Body -->
<div style="padding:1.5rem 2rem">
    <h1 style="font-family:Georgia,serif;font-size:1.2rem;font-weight:900;color:#2C4A2E;margin:0 0 0.3rem">Nouvelle inscription au concours</h1>
    <p style="font-size:0.85rem;color:#6B5D4F;margin:0 0 1.2rem">Un producteur vient de s'inscrire au concours de cidre.</p>

    <!-- Participant info -->
    <div style="border:1.5px solid #F0E8D8;border-radius:12px;padding:1rem 1.2rem;margin-bottom:1rem">
        <table style="width:100%;font-size:0.85rem" cellpadding="0" cellspacing="0" border="0">
            <?php if (!empty($producer)): ?>
            <tr><td style="padding:0.3rem 0;color:#6B5D4F;width:130px;vertical-align:top">Producteur</td><td style="padding:0.3rem 0;font-weight:600;color:#2A2318"><?= $_producer ?></td></tr>
            <?php endif; ?>
            <?php if (!empty($contact_name) || !empty($contact)): ?>
            <tr><td style="padding:0.3rem 0;color:#6B5D4F;vertical-align:top">Responsable</td><td style="padding:0.3rem 0;font-weight:600;color:#2A2318"><?= $_contactName ?></td></tr>
            <?php endif; ?>
            <?php if (!empty($contact_email)): ?>
            <tr><td style="padding:0.3rem 0;color:#6B5D4F;vertical-align:top">E-mail</td><td style="padding:0.3rem 0;font-weight:600;color:#2A2318"><?= $_contactEmail ?></td></tr>
            <?php endif; ?>
            <?php if (!empty($contact_phone)): ?>
            <tr><td style="padding:0.3rem 0;color:#6B5D4F;vertical-align:top">Téléphone</td><td style="padding:0.3rem 0;font-weight:600;color:#2A2318"><?= $_contactPhone ?></td></tr>
            <?php endif; ?>
            <?php if (!empty($contact_address)): ?>
            <tr><td style="padding:0.3rem 0;color:#6B5D4F;vertical-align:top">Adresse</td><td style="padding:0.3rem 0;font-weight:600;color:#2A2318"><?= $_contactAddress ?></td></tr>
            <?php endif; ?>
        </table>
    </div>

    <!-- Products entered -->
    <?php if (!empty($products)): ?>
    <div style="font-size:0.68rem;font-weight:700;color:#6B5D4F;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.3rem">Produits présentés (<?= $_totalProducts ?>)</div>
    <div style="background:#FAF5EC;border-radius:12px;padding:0.1rem 1rem;margin-bottom:1.2rem">
        <?php foreach ($products as $i => $product):
            $cat = strtolower($product['category'] ?? '');
            $catColor = $_categoryColors[$cat] ?? ['bg' => 'rgba(107,93,79,0.1)', 'color' => '#6B5D4F'];
        ?>
        <div style="padding:0.5rem 0;<?= $i < count($products) - 1 ? 'border-bottom:1px solid #F0E8D8;' : '' ?>">
            <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
                <td style="font-size:0.85rem;font-weight:600"><?= e($product['name'] ?? '') ?></td>
                <td style="text-align:right">
                    <span style="font-size:0.72rem;font-weight:700;padding:0.15rem 0.5rem;border-radius:100px;background:<?= $catColor['bg'] ?>;color:<?= $catColor['color'] ?>">Catégorie <?= e($product['category'] ?? '') ?></span>
                </td>
            </tr></table>
        </div>
        <?php endforeach; ?>
    </div>
    <?php endif; ?>

    <!-- Stats -->
    <?php if ($_statsRegistered > 0 || $_statsProducts > 0): ?>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:1.2rem"><tr>
        <td width="32%" style="vertical-align:top">
            <div style="background:#FAF5EC;border-radius:10px;padding:0.6rem 0.8rem;text-align:center">
                <div style="font-size:1.1rem;font-weight:900;color:#2C4A2E;font-family:Georgia,serif"><?= $_statsRegistered ?></div>
                <div style="font-size:0.68rem;color:#6B5D4F;font-weight:600">inscrits</div>
            </div>
        </td>
        <td width="2%"></td>
        <td width="32%" style="vertical-align:top">
            <div style="background:#FAF5EC;border-radius:10px;padding:0.6rem 0.8rem;text-align:center">
                <div style="font-size:1.1rem;font-weight:900;color:#2C4A2E;font-family:Georgia,serif"><?= $_statsProducts ?></div>
                <div style="font-size:0.68rem;color:#6B5D4F;font-weight:600">produits</div>
            </div>
        </td>
        <td width="2%"></td>
        <td width="32%" style="vertical-align:top">
            <div style="background:#FAF5EC;border-radius:10px;padding:0.6rem 0.8rem;text-align:center">
                <div style="font-size:1.1rem;font-weight:900;color:#D4833B;font-family:Georgia,serif">+<?= $_statsWeek ?></div>
                <div style="font-size:0.68rem;color:#6B5D4F;font-weight:600">cette semaine</div>
            </div>
        </td>
    </tr></table>
    <?php endif; ?>

    <div style="text-align:center">
        <a href="<?= e($_baseUrl) ?>/admin/contest" style="display:inline-block;padding:0.75rem 2rem;background:#2C4A2E;color:#FAF5EC;text-decoration:none;border-radius:10px;font-size:0.85rem;font-weight:700">Gérer les inscriptions</a>
    </div>
</div>

<!-- Footer -->
<div style="background:#FAF5EC;padding:0.8rem 2rem;text-align:center;border-top:1px solid #F0E8D8">
    <div style="font-size:0.7rem;color:#6B5D4F">Vous recevez cet e-mail car les notifications concours sont activées dans les paramètres.</div>
</div>
