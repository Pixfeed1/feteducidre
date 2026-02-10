<?php
$_baseUrl = \App\Core\Config::baseUrl();
$_name = e($name ?? '');
$_orderId = e($order_id ?? '');
$_orderDate = e($order_date ?? date('j F Y'));
$_subtotal = number_format((float)($subtotal ?? $total ?? 0), 2, ',', ' ');
$_shippingLabel = e($shipping_label ?? 'Livraison');
$_shippingCost = number_format((float)($shipping_cost ?? 0), 2, ',', ' ');
$_total = number_format((float)($total ?? 0), 2, ',', ' ');
$_taxNote = e($tax_note ?? 'TVA non applicable, art. 293 B du CGI');
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
        <div style="width:56px;height:56px;margin:0 auto 1rem;background:rgba(22,163,74,0.1);border-radius:16px;line-height:56px;text-align:center">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/></svg>
        </div>
        <h1 style="font-family:Georgia,serif;font-size:1.4rem;font-weight:900;color:#2C4A2E;margin:0 0 0.4rem">Merci pour votre commande !</h1>
        <p style="font-size:0.9rem;color:#6B5D4F;margin:0;line-height:1.5">Bonjour <strong style="color:#2A2318"><?= $_name ?></strong>, votre commande a bien été enregistrée.</p>
    </div>

    <!-- Order info -->
    <div style="background:#FAF5EC;border-radius:12px;padding:1rem 1.2rem;margin-bottom:1.2rem">
        <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
            <td>
                <div style="font-size:0.68rem;font-weight:700;color:#6B5D4F;text-transform:uppercase;letter-spacing:0.06em">Commande n°</div>
                <div style="font-size:1.05rem;font-weight:900;color:#2C4A2E;font-family:Georgia,serif"><?= $_orderId ?></div>
            </td>
            <td style="text-align:right">
                <div style="font-size:0.68rem;font-weight:700;color:#6B5D4F;text-transform:uppercase;letter-spacing:0.06em">Date</div>
                <div style="font-size:0.88rem;font-weight:600;color:#2A2318"><?= $_orderDate ?></div>
            </td>
        </tr></table>
    </div>

    <!-- Products table -->
    <?php if (!empty($items)): ?>
    <table style="width:100%;border-collapse:collapse;margin-bottom:1.2rem" cellpadding="0" cellspacing="0">
        <thead>
            <tr style="border-bottom:2px solid #F0E8D8">
                <th style="text-align:left;padding:0.5rem 0;font-size:0.68rem;font-weight:700;color:#6B5D4F;text-transform:uppercase;letter-spacing:0.06em">Produit</th>
                <th style="text-align:center;padding:0.5rem 0;font-size:0.68rem;font-weight:700;color:#6B5D4F;text-transform:uppercase;letter-spacing:0.06em">Qté</th>
                <th style="text-align:right;padding:0.5rem 0;font-size:0.68rem;font-weight:700;color:#6B5D4F;text-transform:uppercase;letter-spacing:0.06em">Prix</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($items as $item): ?>
            <tr style="border-bottom:1px solid #F0E8D8">
                <td style="padding:0.7rem 0">
                    <div style="font-weight:600;font-size:0.88rem;color:#2A2318"><?= e($item['name'] ?? '') ?></div>
                    <?php if (!empty($item['description'])): ?>
                    <div style="font-size:0.75rem;color:#6B5D4F"><?= e($item['description']) ?></div>
                    <?php endif; ?>
                </td>
                <td style="text-align:center;font-size:0.88rem;font-weight:600;color:#2A2318;padding:0.7rem 0">&times;<?= (int)($item['quantity'] ?? 1) ?></td>
                <td style="text-align:right;font-weight:700;color:#2A2318;padding:0.7rem 0"><?= number_format((float)($item['total'] ?? 0), 2, ',', ' ') ?>&nbsp;&euro;</td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
    <?php endif; ?>

    <!-- Totals -->
    <div style="background:#FAF5EC;border-radius:12px;padding:0.8rem 1.2rem">
        <table style="width:100%;font-size:0.85rem" cellpadding="0" cellspacing="0" border="0">
            <tr><td style="padding:0.2rem 0;color:#6B5D4F">Sous-total</td><td style="padding:0.2rem 0;text-align:right;font-weight:600;color:#2A2318"><?= $_subtotal ?>&nbsp;&euro;</td></tr>
            <?php if (!empty($shipping_cost)): ?>
            <tr><td style="padding:0.2rem 0;color:#6B5D4F"><?= $_shippingLabel ?></td><td style="padding:0.2rem 0;text-align:right;font-weight:600;color:#2A2318"><?= $_shippingCost ?>&nbsp;&euro;</td></tr>
            <?php endif; ?>
            <tr><td colspan="2" style="padding:0"><div style="border-top:2px solid #F0E8D8;margin:0.3rem 0"></div></td></tr>
            <tr><td style="padding:0.2rem 0;font-weight:700;font-size:0.95rem;color:#2C4A2E">Total TTC</td><td style="padding:0.2rem 0;text-align:right;font-weight:900;font-size:1.1rem;color:#2C4A2E;font-family:Georgia,serif"><?= $_total ?>&nbsp;&euro;</td></tr>
        </table>
        <?php if (!empty($_taxNote)): ?>
        <div style="font-size:0.72rem;color:#6B5D4F;margin-top:0.2rem"><?= $_taxNote ?></div>
        <?php endif; ?>
    </div>

    <!-- Shipping address -->
    <?php if (!empty($address)): ?>
    <div style="margin-top:1.2rem;padding:1rem 1.2rem;border:1.5px solid #F0E8D8;border-radius:12px">
        <div style="font-size:0.68rem;font-weight:700;color:#6B5D4F;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.4rem">Adresse de livraison</div>
        <div style="font-size:0.88rem;color:#2A2318;line-height:1.5"><?= nl2br(e($address)) ?></div>
    </div>
    <?php endif; ?>

    <!-- Next steps -->
    <div style="margin-top:1.2rem;padding:0.8rem 1rem;background:rgba(44,74,46,0.04);border-radius:10px">
        <table cellpadding="0" cellspacing="0" border="0"><tr>
            <td style="vertical-align:top;padding-right:10px">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4A6B3E" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
            </td>
            <td style="font-size:0.78rem;color:#4A6B3E;line-height:1.5">Votre commande sera préparée et expédiée sous <strong>2 à 5 jours ouvrés</strong>. Vous recevrez un e-mail avec le numéro de suivi.</td>
        </tr></table>
    </div>
</div>

<!-- Footer -->
<div style="background:#FAF5EC;padding:1.2rem 2rem;text-align:center;border-top:1px solid #F0E8D8">
    <div style="font-size:0.78rem;color:#6B5D4F;margin-bottom:0.4rem">Une question sur votre commande ?</div>
    <a href="mailto:<?= e($contact_email ?? 'contact@fetecidre.fr') ?>" style="display:inline-block;padding:0.5rem 1.5rem;background:#2C4A2E;color:#FAF5EC;text-decoration:none;border-radius:10px;font-size:0.82rem;font-weight:600">Nous contacter</a>
    <div style="font-size:0.72rem;color:#6B5D4F;line-height:1.6;margin-top:0.8rem">
        Association La Fête du Cidre — L'Hôtellerie de Flée, 49500<br>
        <a href="<?= e($_baseUrl) ?>" style="color:#D4833B;text-decoration:none">fetecidre.fr</a>
    </div>
</div>
