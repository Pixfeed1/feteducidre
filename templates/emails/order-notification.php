<?php
$_baseUrl = \App\Core\Config::baseUrl();
$_orderId = e($order_id ?? '');
$_amount = number_format((float)($amount ?? 0), 2, ',', ' ');
$_customerName = e($customer_name ?? $customer ?? '');
$_customerEmail = e($customer_email ?? '');
$_customerAddress = e($customer_address ?? '');
$_totalItems = (int)($total_items ?? (is_array($items ?? null) ? count($items) : 0));
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
            <span style="background:#D4833B;color:white;padding:0.3rem 0.8rem;border-radius:100px;font-size:0.72rem;font-weight:700">NOUVELLE COMMANDE</span>
        </td>
    </tr></table>
</div>

<!-- Body -->
<div style="padding:1.5rem 2rem">
    <h1 style="font-family:Georgia,serif;font-size:1.2rem;font-weight:900;color:#2C4A2E;margin:0 0 0.3rem">Nouvelle commande reçue</h1>
    <p style="font-size:0.85rem;color:#6B5D4F;margin:0 0 1.2rem">Une commande vient d'être passée sur la boutique.</p>

    <!-- Summary grid -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:1.2rem"><tr>
        <td width="49%" style="vertical-align:top">
            <div style="background:#FAF5EC;border-radius:10px;padding:0.7rem 0.9rem">
                <div style="font-size:0.65rem;font-weight:700;color:#6B5D4F;text-transform:uppercase;letter-spacing:0.06em">Commande</div>
                <div style="font-size:1rem;font-weight:900;color:#2C4A2E;font-family:Georgia,serif"><?= $_orderId ?></div>
            </div>
        </td>
        <td width="2%"></td>
        <td width="49%" style="vertical-align:top">
            <div style="background:#FAF5EC;border-radius:10px;padding:0.7rem 0.9rem">
                <div style="font-size:0.65rem;font-weight:700;color:#6B5D4F;text-transform:uppercase;letter-spacing:0.06em">Montant</div>
                <div style="font-size:1rem;font-weight:900;color:#D4833B;font-family:Georgia,serif"><?= $_amount ?>&nbsp;&euro;</div>
            </div>
        </td>
    </tr></table>

    <!-- Client info -->
    <div style="border:1.5px solid #F0E8D8;border-radius:12px;padding:0.8rem 1rem;margin-bottom:1rem">
        <div style="font-size:0.68rem;font-weight:700;color:#6B5D4F;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.3rem">Client</div>
        <div style="font-size:0.88rem;color:#2A2318;line-height:1.6">
            <strong><?= $_customerName ?></strong>
            <?php if (!empty($customer_email)): ?><br><?= $_customerEmail ?><?php endif; ?>
            <?php if (!empty($customer_address)): ?><br><?= $_customerAddress ?><?php endif; ?>
        </div>
    </div>

    <!-- Products -->
    <?php if (!empty($items)): ?>
    <div style="font-size:0.68rem;font-weight:700;color:#6B5D4F;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.3rem">Articles (<?= $_totalItems ?>)</div>
    <div style="border:1.5px solid #F0E8D8;border-radius:12px;padding:0.1rem 1rem;margin-bottom:1.2rem">
        <?php foreach ($items as $i => $item): ?>
        <div style="padding:0.5rem 0;<?= $i < count($items) - 1 ? 'border-bottom:1px solid #F0E8D8;' : '' ?>">
            <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
                <td style="font-size:0.85rem"><?= e($item['name'] ?? '') ?> <span style="color:#6B5D4F">&times;<?= (int)($item['quantity'] ?? 1) ?></span></td>
                <td style="text-align:right;font-size:0.85rem;font-weight:700"><?= number_format((float)($item['total'] ?? 0), 2, ',', ' ') ?>&nbsp;&euro;</td>
            </tr></table>
        </div>
        <?php endforeach; ?>
    </div>
    <?php endif; ?>

    <!-- CTA -->
    <div style="text-align:center">
        <a href="<?= e($_baseUrl) ?>/admin/orders" style="display:inline-block;padding:0.75rem 2rem;background:#2C4A2E;color:#FAF5EC;text-decoration:none;border-radius:10px;font-size:0.85rem;font-weight:700">Voir la commande dans l'admin</a>
    </div>
</div>

<!-- Footer -->
<div style="background:#FAF5EC;padding:0.8rem 2rem;text-align:center;border-top:1px solid #F0E8D8">
    <div style="font-size:0.7rem;color:#6B5D4F">Vous recevez cet e-mail car vous êtes administrateur de la Fête du Cidre.</div>
</div>
