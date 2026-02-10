<?php
$_baseUrl = \App\Core\Config::baseUrl();
$_name = e($name ?? '');
$_orderId = e($order_id ?? '');
$_tracking = e($tracking ?? '');
$_carrier = e($carrier ?? 'Colissimo');
$_trackingUrl = e($tracking_url ?? '#');
$_address = e($address ?? '');
$_orderDate = e($order_date ?? '');
$_shippedDate = e($shipped_date ?? date('j F Y'));
$_eta = e($eta ?? '');
?>
<!-- Header -->
<div style="background:#2C4A2E;padding:2rem 2rem 1.6rem;text-align:center">
    <div style="width:52px;height:52px;margin:0 auto 0.8rem;background:#4A6B3E;border-radius:14px;line-height:52px;text-align:center">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" style="vertical-align:middle"><circle cx="12" cy="14" r="8" fill="#7A9E6B"/><ellipse cx="12" cy="13" rx="5" ry="7" fill="#A3C48E"/><path d="M12 3c-1-2 1-3 2-1" stroke="#D4C4A0" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg>
    </div>
    <div style="font-family:Georgia,serif;font-size:1.3rem;font-weight:900;color:#FAF5EC">Fête du Cidre</div>
    <div style="font-size:0.72rem;color:rgba(250,245,236,0.5);letter-spacing:0.1em;text-transform:uppercase;margin-top:2px">L'Hôtellerie de Flée</div>
</div>

<!-- Body -->
<div style="padding:2rem 2rem 1.5rem">
    <div style="text-align:center;margin-bottom:1.5rem">
        <div style="width:56px;height:56px;margin:0 auto 1rem;background:rgba(212,131,59,0.1);border-radius:16px;line-height:56px;text-align:center">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#D4833B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 13.52 8H12"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg>
        </div>
        <h1 style="font-family:Georgia,serif;font-size:1.4rem;font-weight:900;color:#2C4A2E;margin:0 0 0.4rem">Votre colis est en route !</h1>
        <p style="font-size:0.9rem;color:#6B5D4F;margin:0;line-height:1.5">Bonjour <strong style="color:#2A2318"><?= $_name ?></strong>, votre commande <strong style="color:#2C4A2E"><?= $_orderId ?></strong> a été expédiée.</p>
    </div>

    <!-- Tracking -->
    <?php if (!empty($tracking)): ?>
    <div style="background:linear-gradient(135deg,#2C4A2E,#4A6B3E);border-radius:14px;padding:1.2rem 1.4rem;margin-bottom:1.2rem;text-align:center">
        <div style="font-size:0.68rem;font-weight:700;color:rgba(250,245,236,0.6);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem">Numéro de suivi <?= e($carrier ?? 'Colissimo') ?></div>
        <div style="font-size:1.3rem;font-weight:900;color:#FAF5EC;letter-spacing:0.15em;font-family:'Source Sans 3',monospace;margin-bottom:0.8rem"><?= $_tracking ?></div>
        <a href="<?= $_trackingUrl ?>" style="display:inline-block;padding:0.6rem 1.8rem;background:#D4833B;color:white;text-decoration:none;border-radius:10px;font-size:0.85rem;font-weight:700">Suivre mon colis</a>
    </div>
    <?php endif; ?>

    <!-- Timeline -->
    <div style="margin-bottom:1.2rem;padding:0 0.5rem">
        <?php if (!empty($order_date)): ?>
        <table cellpadding="0" cellspacing="0" border="0" style="margin-bottom:0.8rem"><tr>
            <td width="24" style="vertical-align:top">
                <div style="width:24px;height:24px;background:#16a34a;border-radius:50%;line-height:24px;text-align:center">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" style="vertical-align:middle"><path d="M20 6 9 17l-5-5"/></svg>
                </div>
            </td>
            <td style="padding-left:12px;vertical-align:top">
                <div style="font-size:0.85rem;font-weight:700;color:#2A2318">Commande confirmée</div>
                <div style="font-size:0.75rem;color:#6B5D4F"><?= $_orderDate ?></div>
            </td>
        </tr></table>
        <div style="width:2px;height:16px;background:#F0E8D8;margin-left:11px;margin-bottom:0.4rem"></div>
        <?php endif; ?>

        <table cellpadding="0" cellspacing="0" border="0" style="margin-bottom:0.8rem"><tr>
            <td width="24" style="vertical-align:top">
                <div style="width:24px;height:24px;background:#16a34a;border-radius:50%;line-height:24px;text-align:center">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" style="vertical-align:middle"><path d="M20 6 9 17l-5-5"/></svg>
                </div>
            </td>
            <td style="padding-left:12px;vertical-align:top">
                <div style="font-size:0.85rem;font-weight:700;color:#2A2318">Colis expédié</div>
                <div style="font-size:0.75rem;color:#6B5D4F"><?= $_shippedDate ?></div>
            </td>
        </tr></table>

        <?php if (!empty($eta)): ?>
        <div style="width:2px;height:16px;background:#F0E8D8;margin-left:11px;margin-bottom:0.4rem"></div>
        <table cellpadding="0" cellspacing="0" border="0"><tr>
            <td width="24" style="vertical-align:top">
                <div style="width:24px;height:24px;background:#F0E8D8;border-radius:50%;line-height:24px;text-align:center">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#6B5D4F" stroke-width="2" stroke-linecap="round" style="vertical-align:middle"><circle cx="12" cy="12" r="10"/></svg>
                </div>
            </td>
            <td style="padding-left:12px;vertical-align:top">
                <div style="font-size:0.85rem;font-weight:600;color:#6B5D4F">Livraison estimée</div>
                <div style="font-size:0.85rem;font-weight:700;color:#D4833B"><?= $_eta ?></div>
            </td>
        </tr></table>
        <?php endif; ?>
    </div>

    <!-- Shipping address -->
    <?php if (!empty($address)): ?>
    <div style="padding:0.8rem 1rem;background:#FAF5EC;border-radius:10px">
        <div style="font-size:0.68rem;font-weight:700;color:#6B5D4F;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.2rem">Adresse de livraison</div>
        <div style="font-size:0.82rem;color:#2A2318;line-height:1.5"><?= nl2br(e($address)) ?></div>
    </div>
    <?php endif; ?>
</div>

<!-- Footer -->
<div style="background:#FAF5EC;padding:1.2rem 2rem;text-align:center;border-top:1px solid #F0E8D8">
    <div style="font-size:0.78rem;color:#6B5D4F;margin-bottom:0.4rem">Une question ?</div>
    <a href="mailto:<?= e($contact_email ?? 'contact@fetecidre.fr') ?>" style="color:#D4833B;text-decoration:none;font-size:0.82rem;font-weight:600"><?= e($contact_email ?? 'contact@fetecidre.fr') ?></a>
    <div style="font-size:0.72rem;color:#6B5D4F;line-height:1.6;margin-top:0.6rem">
        Association La Fête du Cidre — L'Hôtellerie de Flée, 49500
    </div>
</div>
