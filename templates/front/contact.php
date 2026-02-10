<?php
/**
 * Template page de contact.
 * Variables : $page, $seo, $settings
 */
$address = $settings['general']['association_address'] ?? 'L\'Hôtellerie de Flée, 49500';
$email = $settings['general']['association_email'] ?? 'contact@fetecidre.fr';
$phone = $settings['general']['association_phone'] ?? '';
$siteName = $settings['general']['association_name'] ?? 'Association Fête du Cidre';
?>

<!-- Page Hero -->
<section class="page-hero">
    <div class="page-hero-pattern"></div>
    <div class="page-hero-decoration"></div>
    <div class="container">
        <span class="page-hero-badge">
            <?= icon('mail', 16) ?> Contact
        </span>

        <h1 class="page-hero-title">Nous <em>contacter</em></h1>

        <p class="page-hero-intro">Une question ? N'hésitez pas à nous écrire</p>
    </div>
</section>

<?php if (!empty($page['content'])): ?>
<section class="section" style="padding-bottom:0">
    <div class="container cms-content">
        <?= sanitize($page['content']) ?>
    </div>
</section>
<?php endif; ?>

<section class="section">
    <div class="container">
        <div class="contact-layout" style="display:grid;grid-template-columns:1fr 380px;gap:3rem;align-items:start">

            <!-- Formulaire de contact -->
            <div class="contact-form">
                <div class="card">
                    <div class="card-body" style="padding:2rem">
                        <h2 style="margin-bottom:1.5rem">Envoyez-nous un message</h2>

                        <form action="/contact" method="post">
                            <?= csrf_field() ?>

                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem">
                                <div class="form-group">
                                    <label for="name">Nom <span style="color:var(--orange-cidre)">*</span></label>
                                    <input type="text" name="name" id="name"
                                           value="<?= old('name') ?>" required
                                           class="form-control" placeholder="Votre nom">
                                </div>
                                <div class="form-group">
                                    <label for="email">Email <span style="color:var(--orange-cidre)">*</span></label>
                                    <input type="email" name="email" id="email"
                                           value="<?= old('email') ?>" required
                                           class="form-control" placeholder="votre@email.fr">
                                </div>
                            </div>

                            <div class="form-group" style="margin-bottom:1rem">
                                <label for="subject">Sujet</label>
                                <input type="text" name="subject" id="subject"
                                       value="<?= old('subject') ?>"
                                       class="form-control" placeholder="Objet de votre message">
                            </div>

                            <div class="form-group" style="margin-bottom:1.5rem">
                                <label for="message">Message <span style="color:var(--orange-cidre)">*</span></label>
                                <textarea name="message" id="message" rows="6" required
                                          class="form-control" placeholder="Votre message..."><?= old('message') ?></textarea>
                            </div>

                            <button type="submit" class="btn btn-secondary" style="width:100%;justify-content:center">
                                <?= icon('mail', 18) ?> Envoyer le message
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Encart coordonnées -->
            <div class="contact-info">
                <div class="card">
                    <div class="card-body" style="padding:1.5rem">
                        <h3 style="margin-bottom:1.5rem">Nos coordonnées</h3>

                        <div style="margin-bottom:1.25rem;display:flex;align-items:start;gap:.75rem">
                            <span style="flex-shrink:0;margin-top:2px"><?= icon('map-pin', 20, '', 'var(--vert-mousse)') ?></span>
                            <div>
                                <strong>Adresse</strong>
                                <p style="color:var(--brun);margin-top:.25rem"><?= e($address) ?></p>
                            </div>
                        </div>

                        <div style="margin-bottom:1.25rem;display:flex;align-items:start;gap:.75rem">
                            <span style="flex-shrink:0;margin-top:2px"><?= icon('mail', 20, '', 'var(--vert-mousse)') ?></span>
                            <div>
                                <strong>Email</strong>
                                <p style="margin-top:.25rem">
                                    <a href="mailto:<?= e($email) ?>"><?= e($email) ?></a>
                                </p>
                            </div>
                        </div>

                        <?php if ($phone): ?>
                            <div style="margin-bottom:1.25rem;display:flex;align-items:start;gap:.75rem">
                                <span style="flex-shrink:0;margin-top:2px"><?= icon('phone', 20, '', 'var(--vert-mousse)') ?></span>
                                <div>
                                    <strong>Téléphone</strong>
                                    <p style="margin-top:.25rem">
                                        <a href="tel:<?= e(phone_clean($phone)) ?>"><?= e($phone) ?></a>
                                    </p>
                                </div>
                            </div>
                        <?php endif; ?>

                        <?php
                        $facebookUrl = $settings['social']['facebook_url'] ?? '';
                        $instagramUrl = $settings['social']['instagram_url'] ?? '';
                        ?>
                        <?php if ($facebookUrl || $instagramUrl): ?>
                            <hr style="border:none;border-top:1px solid var(--creme-fonce);margin:1.5rem 0">
                            <h4 style="margin-bottom:.75rem">Suivez-nous</h4>
                            <div style="display:flex;gap:1rem">
                                <?php if ($facebookUrl): ?>
                                    <a href="<?= e($facebookUrl) ?>" target="_blank" rel="noopener noreferrer"
                                       style="display:flex;align-items:center;gap:.5rem;color:var(--vert-profond);font-weight:500">
                                        <?= icon('facebook', 20) ?> Facebook
                                    </a>
                                <?php endif; ?>
                                <?php if ($instagramUrl): ?>
                                    <a href="<?= e($instagramUrl) ?>" target="_blank" rel="noopener noreferrer"
                                       style="display:flex;align-items:center;gap:.5rem;color:var(--vert-profond);font-weight:500">
                                        <?= icon('instagram', 20) ?> Instagram
                                    </a>
                                <?php endif; ?>
                            </div>
                        <?php endif; ?>
                    </div>
                </div>

                <!-- Encart association -->
                <div class="card" style="margin-top:1.5rem">
                    <div class="card-body" style="padding:1.5rem;text-align:center">
                        <?= icon('apple', 28, '', 'var(--vert-profond)') ?>
                        <p style="margin-top:.75rem;font-weight:600;color:var(--vert-profond)"><?= e($siteName) ?></p>
                        <p style="font-size:.85rem;color:var(--brun);margin-top:.25rem">Association loi 1901 — Depuis 1989</p>
                    </div>
                </div>
            </div>

        </div>
    </div>
</section>
