<?php
/**
 * Template formulaire de commande.
 * Variables : $items, $subtotal, $shipping, $total, $seo
 */
?>

<!-- En-tête de page -->
<section class="page-header">
    <div class="container">
        <h1><?= icon('package', 32) ?> Finaliser la commande</h1>
    </div>
</section>

<section class="section section-checkout">
    <div class="container">
        <form action="/commande" method="post" class="checkout-form">
            <?= csrf_field() ?>

            <div class="checkout-layout" style="display:grid;grid-template-columns:1fr 380px;gap:2rem;align-items:start">

                <!-- Formulaire adresse -->
                <div class="checkout-fields">
                    <div class="card">
                        <div class="card-body" style="padding:2rem">
                            <h2 style="margin-bottom:1.5rem"><?= icon('user', 22) ?> Vos coordonnées</h2>

                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem">
                                <div class="form-group">
                                    <label for="first_name">Prénom <span style="color:var(--orange-cidre)">*</span></label>
                                    <input type="text" name="first_name" id="first_name"
                                           value="<?= old('first_name') ?>" required
                                           class="form-input" placeholder="Votre prénom">
                                </div>
                                <div class="form-group">
                                    <label for="last_name">Nom <span style="color:var(--orange-cidre)">*</span></label>
                                    <input type="text" name="last_name" id="last_name"
                                           value="<?= old('last_name') ?>" required
                                           class="form-input" placeholder="Votre nom">
                                </div>
                            </div>

                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem">
                                <div class="form-group">
                                    <label for="email">Email <span style="color:var(--orange-cidre)">*</span></label>
                                    <input type="email" name="email" id="email"
                                           value="<?= old('email') ?>" required
                                           class="form-input" placeholder="votre@email.fr">
                                </div>
                                <div class="form-group">
                                    <label for="phone">Téléphone</label>
                                    <input type="tel" name="phone" id="phone"
                                           value="<?= old('phone') ?>"
                                           class="form-input" placeholder="06 12 34 56 78">
                                </div>
                            </div>

                            <h2 style="margin-top:2rem;margin-bottom:1.5rem"><?= icon('map-pin', 22) ?> Adresse de livraison</h2>

                            <div class="form-group">
                                <label for="address">Adresse <span style="color:var(--orange-cidre)">*</span></label>
                                <input type="text" name="address" id="address"
                                       value="<?= old('address') ?>" required
                                       class="form-input" placeholder="Numéro et nom de rue">
                            </div>

                            <div style="display:grid;grid-template-columns:2fr 1fr;gap:1rem;margin-top:1rem">
                                <div class="form-group">
                                    <label for="city">Ville <span style="color:var(--orange-cidre)">*</span></label>
                                    <input type="text" name="city" id="city"
                                           value="<?= old('city') ?>" required
                                           class="form-input" placeholder="Ville">
                                </div>
                                <div class="form-group">
                                    <label for="postal_code">Code postal <span style="color:var(--orange-cidre)">*</span></label>
                                    <input type="text" name="postal_code" id="postal_code"
                                           value="<?= old('postal_code') ?>" required
                                           class="form-input" placeholder="49000" maxlength="5" pattern="[0-9]{5}">
                                </div>
                            </div>

                            <div class="form-group" style="margin-top:1rem">
                                <label for="notes">Notes de commande</label>
                                <textarea name="notes" id="notes" rows="3" class="form-input"
                                          placeholder="Instructions particulières pour la livraison..."><?= old('notes') ?></textarea>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Récapitulatif de commande -->
                <div class="checkout-summary">
                    <div class="card" style="position:sticky;top:2rem">
                        <div class="card-body" style="padding:1.5rem">
                            <h3 style="margin-bottom:1.5rem">Récapitulatif</h3>

                            <?php foreach ($items as $item): ?>
                                <div style="display:flex;justify-content:space-between;margin-bottom:.75rem;font-size:.95rem">
                                    <span>
                                        <?= e($item['product']['name']) ?>
                                        <small style="color:var(--brun)">&times;<?= $item['quantity'] ?></small>
                                    </span>
                                    <span style="font-weight:600;white-space:nowrap"><?= number_format($item['total'], 2, ',', ' ') ?> &euro;</span>
                                </div>
                            <?php endforeach; ?>

                            <hr style="border:none;border-top:1px solid var(--creme-fonce);margin:1rem 0">

                            <div style="display:flex;justify-content:space-between;margin-bottom:.5rem">
                                <span>Sous-total</span>
                                <span style="font-weight:600"><?= number_format($subtotal, 2, ',', ' ') ?> &euro;</span>
                            </div>
                            <div style="display:flex;justify-content:space-between;margin-bottom:.5rem">
                                <span><?= icon('truck', 16) ?> Livraison</span>
                                <span style="font-weight:600"><?= number_format($shipping, 2, ',', ' ') ?> &euro;</span>
                            </div>

                            <hr style="border:none;border-top:2px solid var(--creme-fonce);margin:1rem 0">

                            <div style="display:flex;justify-content:space-between;font-size:1.2rem">
                                <strong>Total</strong>
                                <strong style="color:var(--orange-cidre)"><?= number_format($total, 2, ',', ' ') ?> &euro;</strong>
                            </div>

                            <button type="submit" class="btn btn-secondary" style="width:100%;justify-content:center;margin-top:1.5rem">
                                <?= icon('check', 18) ?> Valider la commande
                            </button>

                            <p style="font-size:.8rem;color:var(--brun);text-align:center;margin-top:1rem">
                                <?= icon('shield', 14) ?> Paiement sécurisé — Vos données sont protégées
                            </p>
                        </div>
                    </div>
                </div>

            </div>
        </form>
    </div>
</section>
