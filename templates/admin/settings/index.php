<?php
/**
 * Paramètres — administration (8 onglets).
 * Variables : $settings, $currentTab, $tabs, $tabIcons, $colors, $defaultColors
 */

/** Raccourci pour lire une valeur de paramètre */
function sv(array $settings, string $group, string $key, string $default = ''): string
{
    return $settings[$group][$key]['value'] ?? $default;
}
?>

<!-- ===== Page header ===== -->
<div class="page-header">
    <div class="page-header-icon" style="background:rgba(44,74,46,0.1);">
        <?= icon('settings', 28, '', '#2C4A2E') ?>
    </div>
    <div>
        <h1>Paramètres</h1>
        <p class="page-subtitle">Configuration générale du site et de l'association</p>
    </div>
</div>

<!-- ===== Tabs navigation ===== -->
<div class="settings-tabs">
    <?php foreach ($tabs as $key => $label): ?>
        <button type="button" class="stab <?= $currentTab === $key ? 'active' : '' ?>" onclick="switchTab('<?= $key ?>')">
            <?= icon($tabIcons[$key] ?? 'settings', 16) ?>
            <?= $label ?>
        </button>
    <?php endforeach; ?>
</div>

<!-- ================================================================
     TAB: Général
     ================================================================ -->
<div class="settings-section <?= $currentTab === 'general' ? 'active' : '' ?>" id="tab-general">
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="general">

        <!-- Association -->
        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('building-2', 18) ?> Informations de l'association</div>
                <div class="fields-grid">
                    <div class="form-group">
                        <label class="field-label" for="association_name">Nom de l'association</label>
                        <input type="text" id="association_name" name="association_name" class="form-control"
                               value="<?= e(sv($settings, 'general', 'association_name', 'Association Fête du Cidre')) ?>">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="site_name">Nom court / Marque</label>
                        <input type="text" id="site_name" name="site_name" class="form-control"
                               value="<?= e(sv($settings, 'general', 'site_name', 'Fête du Cidre')) ?>">
                    </div>
                    <div class="form-group full">
                        <label class="field-label" for="association_address">Adresse</label>
                        <input type="text" id="association_address" name="association_address" class="form-control"
                               value="<?= e(sv($settings, 'general', 'association_address')) ?>"
                               placeholder="Parc du Drugeot, L'Hôtellerie de Flée, 49500">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="association_postal">Code postal</label>
                        <input type="text" id="association_postal" name="association_postal" class="form-control"
                               value="<?= e(sv($settings, 'general', 'association_postal', '49500')) ?>">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="association_siret">SIRET</label>
                        <input type="text" id="association_siret" name="association_siret" class="form-control"
                               value="<?= e(sv($settings, 'general', 'association_siret')) ?>"
                               placeholder="123 456 789 00012">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="association_rna">N° RNA</label>
                        <input type="text" id="association_rna" name="association_rna" class="form-control"
                               value="<?= e(sv($settings, 'general', 'association_rna')) ?>"
                               placeholder="W491234567">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="association_phone">Téléphone</label>
                        <input type="text" id="association_phone" name="association_phone" class="form-control"
                               value="<?= e(sv($settings, 'general', 'association_phone')) ?>"
                               placeholder="02 41 XX XX XX">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="association_email">Email de contact</label>
                        <input type="email" id="association_email" name="association_email" class="form-control"
                               value="<?= e(sv($settings, 'general', 'association_email')) ?>"
                               placeholder="contact@fetecidre.fr">
                    </div>
                    <div class="form-group full">
                        <label class="field-label" for="site_description">Description courte</label>
                        <textarea id="site_description" name="site_description" class="form-control" rows="2"><?= e(sv($settings, 'general', 'site_description')) ?></textarea>
                    </div>
                </div>
            </div>
        </div>

        <!-- Prochaine édition -->
        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('calendar', 18) ?> Prochaine édition</div>
                <div class="fields-grid">
                    <div class="form-group">
                        <label class="field-label" for="next_event_date">Date(s) de l'événement</label>
                        <input type="text" id="next_event_date" name="next_event_date" class="form-control"
                               value="<?= e(sv($settings, 'general', 'next_event_date')) ?>"
                               placeholder="Dimanche 14 Juin 2026">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="next_event_venue">Lieu</label>
                        <input type="text" id="next_event_venue" name="next_event_venue" class="form-control"
                               value="<?= e(sv($settings, 'general', 'next_event_venue', 'Parc du Drugeot')) ?>">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="next_event_time">Horaires</label>
                        <input type="text" id="next_event_time" name="next_event_time" class="form-control"
                               value="<?= e(sv($settings, 'general', 'next_event_time')) ?>"
                               placeholder="10h00 - 19h00">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="next_event_price">Tarif entrée</label>
                        <input type="text" id="next_event_price" name="next_event_price" class="form-control"
                               value="<?= e(sv($settings, 'general', 'next_event_price')) ?>"
                               placeholder="Gratuit">
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary"><?= icon('save', 18) ?> Enregistrer</button>
            </div>
        </div>
    </form>
</div>

<!-- ================================================================
     TAB: Identité
     ================================================================ -->
<div class="settings-section <?= $currentTab === 'identity' ? 'active' : '' ?>" id="tab-identity">

    <!-- Logo -->
    <div class="card">
        <div class="card-body">
            <div class="settings-card-title"><?= icon('image', 18) ?> Logo du site</div>
            <?php $logoFile = sv($settings, 'identity', 'logo_filename'); ?>
            <div class="upload-block">
                <div class="upload-preview">
                    <?php if ($logoFile): ?>
                        <img src="/uploads/settings/<?= e($logoFile) ?>" alt="Logo">
                    <?php else: ?>
                        <?= icon('image', 32, '', '#ccc') ?>
                    <?php endif; ?>
                </div>
                <div class="upload-info">
                    <p>Format recommandé : PNG ou SVG, fond transparent, min 200x200px</p>
                    <div class="upload-actions">
                        <form method="post" action="/admin/settings/upload/logo" enctype="multipart/form-data" style="display:inline;">
                            <?= csrf_field() ?>
                            <label class="btn btn-sm btn-secondary" style="cursor:pointer;">
                                <?= icon('upload', 14) ?> Changer
                                <input type="file" name="logo_file" accept="image/*" style="display:none;" onchange="this.form.submit()">
                            </label>
                        </form>
                        <?php if ($logoFile): ?>
                            <form method="post" action="/admin/settings/remove/logo" style="display:inline;">
                                <?= csrf_field() ?>
                                <button type="submit" class="btn btn-sm btn-secondary" style="color:#c0392b;" onclick="return confirm('Supprimer le logo ?')">
                                    <?= icon('trash-2', 14) ?> Supprimer
                                </button>
                            </form>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Favicon -->
    <div class="card">
        <div class="card-body">
            <div class="settings-card-title"><?= icon('image', 18) ?> Favicon</div>
            <?php $faviconFile = sv($settings, 'identity', 'favicon_filename'); ?>
            <div class="upload-block">
                <div class="upload-preview small">
                    <?php if ($faviconFile): ?>
                        <img src="/uploads/settings/<?= e($faviconFile) ?>" alt="Favicon">
                    <?php else: ?>
                        <?= icon('image', 20, '', '#ccc') ?>
                    <?php endif; ?>
                </div>
                <div class="upload-info">
                    <p>Format : ICO, PNG ou SVG, 32x32 ou 64x64px</p>
                    <div class="upload-actions">
                        <form method="post" action="/admin/settings/upload/favicon" enctype="multipart/form-data" style="display:inline;">
                            <?= csrf_field() ?>
                            <label class="btn btn-sm btn-secondary" style="cursor:pointer;">
                                <?= icon('upload', 14) ?> Changer
                                <input type="file" name="favicon_file" accept="image/*,.ico" style="display:none;" onchange="this.form.submit()">
                            </label>
                        </form>
                        <?php if ($faviconFile): ?>
                            <form method="post" action="/admin/settings/remove/favicon" style="display:inline;">
                                <?= csrf_field() ?>
                                <button type="submit" class="btn btn-sm btn-secondary" style="color:#c0392b;" onclick="return confirm('Supprimer le favicon ?')">
                                    <?= icon('trash-2', 14) ?> Supprimer
                                </button>
                            </form>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Couleurs -->
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="colors">
        <div class="card">
            <div class="card-body">
                <div class="settings-card-title">
                    <?= icon('palette', 18) ?> Charte graphique
                    <div style="margin-left:auto;">
                        <a href="#" onclick="event.preventDefault();document.getElementById('reset-colors-form').submit();" style="font-size:0.75rem;color:#999;font-weight:400;">
                            <?= icon('rotate-ccw', 12) ?> Réinitialiser
                        </a>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:0.75rem;">
                    <?php foreach ($defaultColors as $name => $defaultHex):
                        $currentHex = $colors[$name] ?? $defaultHex;
                        $label = ucfirst(str_replace('-', ' ', $name));
                    ?>
                        <div class="color-row">
                            <div class="color-input-wrap">
                                <input type="color" name="<?= e($name) ?>" value="<?= e($currentHex) ?>">
                            </div>
                            <div>
                                <div class="color-label"><?= e($label) ?></div>
                                <div class="color-hex"><?= e($currentHex) ?></div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary"><?= icon('save', 18) ?> Enregistrer les couleurs</button>
            </div>
        </div>
    </form>
    <form id="reset-colors-form" method="post" action="/admin/settings/colors/reset" style="display:none;">
        <?= csrf_field() ?>
    </form>

    <!-- Typographie -->
    <div class="card">
        <div class="card-body">
            <div class="settings-card-title"><?= icon('type', 18) ?> Typographie</div>
            <div class="fields-grid">
                <div class="form-group">
                    <label class="field-label">Police principale</label>
                    <div style="font-size:1.5rem;font-weight:700;color:#2C4A2E;margin:0.25rem 0;">Playfair Display</div>
                    <div class="field-hint">Utilisée pour les titres et le branding</div>
                </div>
                <div class="form-group">
                    <label class="field-label">Police de corps</label>
                    <div style="font-size:1.5rem;font-weight:400;color:#333;margin:0.25rem 0;">Inter</div>
                    <div class="field-hint">Utilisée pour le texte courant et l'interface</div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- ================================================================
     TAB: SEO
     ================================================================ -->
<div class="settings-section <?= $currentTab === 'seo' ? 'active' : '' ?>" id="tab-seo">
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="seo">

        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('globe', 18) ?> Métadonnées générales</div>
                <div class="fields-grid">
                    <div class="form-group full">
                        <label class="field-label" for="meta_title">Titre du site (balise title)</label>
                        <input type="text" id="meta_title" name="meta_title" class="form-control"
                               value="<?= e(sv($settings, 'seo', 'meta_title', sv($settings, 'general', 'site_name'))) ?>"
                               placeholder="Fête du Cidre — L'Hôtellerie de Flée">
                        <div class="field-hint">Recommandé : 50-60 caractères</div>
                    </div>
                    <div class="form-group full">
                        <label class="field-label" for="meta_description">Meta description</label>
                        <textarea id="meta_description" name="meta_description" class="form-control" rows="2"
                                  placeholder="Description pour les moteurs de recherche..."><?= e(sv($settings, 'seo', 'meta_description')) ?></textarea>
                        <div class="field-hint">Recommandé : 150-160 caractères</div>
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="canonical_url">URL canonique</label>
                        <input type="url" id="canonical_url" name="canonical_url" class="form-control"
                               value="<?= e(sv($settings, 'seo', 'canonical_url')) ?>"
                               placeholder="https://www.fetecidre.fr">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="site_language">Langue du site</label>
                        <select id="site_language" name="site_language" class="form-control">
                            <option value="fr" <?= sv($settings, 'seo', 'site_language', 'fr') === 'fr' ? 'selected' : '' ?>>Français</option>
                            <option value="en" <?= sv($settings, 'seo', 'site_language') === 'en' ? 'selected' : '' ?>>English</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('share-2', 18) ?> Open Graph (réseaux sociaux)</div>
                <div class="fields-grid">
                    <div class="form-group full">
                        <label class="field-label" for="og_title">Titre OG</label>
                        <input type="text" id="og_title" name="og_title" class="form-control"
                               value="<?= e(sv($settings, 'seo', 'og_title')) ?>"
                               placeholder="Fête du Cidre — L'Hôtellerie de Flée">
                    </div>
                    <div class="form-group full">
                        <label class="field-label" for="og_description">Description OG</label>
                        <textarea id="og_description" name="og_description" class="form-control" rows="2"
                                  placeholder="Description pour les partages sociaux..."><?= e(sv($settings, 'seo', 'og_description')) ?></textarea>
                    </div>
                    <div class="form-group full">
                        <label class="field-label" for="og_image">Image OG (URL)</label>
                        <input type="url" id="og_image" name="og_image" class="form-control"
                               value="<?= e(sv($settings, 'seo', 'og_image')) ?>"
                               placeholder="https://www.fetecidre.fr/images/og-image.jpg">
                        <div class="field-hint">Format recommandé : 1200x630 pixels, JPG ou PNG</div>
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary"><?= icon('save', 18) ?> Enregistrer</button>
            </div>
        </div>
    </form>
</div>

<!-- ================================================================
     TAB: Réseaux
     ================================================================ -->
<div class="settings-section <?= $currentTab === 'social' ? 'active' : '' ?>" id="tab-social">
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="social">

        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('share-2', 18) ?> Réseaux sociaux</div>

                <?php
                $socials = [
                    ['key' => 'facebook_url',  'label' => 'Facebook',  'icon' => 'facebook',  'class' => 'fb', 'placeholder' => 'https://facebook.com/fetecidre'],
                    ['key' => 'instagram_url', 'label' => 'Instagram', 'icon' => 'instagram', 'class' => 'ig', 'placeholder' => 'https://instagram.com/fetecidre'],
                    ['key' => 'youtube_url',   'label' => 'YouTube',   'icon' => 'youtube',   'class' => 'yt', 'placeholder' => 'https://youtube.com/@fetecidre'],
                    ['key' => 'twitter_url',   'label' => 'X (Twitter)','icon' => 'twitter',  'class' => 'tw', 'placeholder' => 'https://x.com/fetecidre'],
                    ['key' => 'pinterest_url', 'label' => 'Pinterest', 'icon' => 'pinterest', 'class' => 'pi', 'placeholder' => 'https://pinterest.fr/fetecidre'],
                    ['key' => 'linkedin_url',  'label' => 'LinkedIn',  'icon' => 'linkedin',  'class' => 'li', 'placeholder' => 'https://linkedin.com/company/fetecidre'],
                ];
                foreach ($socials as $s):
                    $val = sv($settings, 'social', $s['key']);
                    $activeKey = $s['key'] . '_active';
                    $isActive = sv($settings, 'social', $activeKey, '1');
                ?>
                    <div class="social-row">
                        <div class="social-icon <?= $s['class'] ?>">
                            <?= icon($s['icon'], 18, '', '#fff') ?>
                        </div>
                        <div class="social-input">
                            <input type="url" name="<?= $s['key'] ?>" class="form-control"
                                   value="<?= e($val) ?>" placeholder="<?= e($s['placeholder']) ?>">
                        </div>
                        <div class="social-toggle">
                            <input type="hidden" name="<?= $activeKey ?>" value="0">
                            <button type="button" class="toggle-switch <?= $isActive === '1' ? 'active' : '' ?>"
                                    onclick="toggleSwitch(this, '<?= $activeKey ?>')">
                                <span class="toggle-slider"></span>
                            </button>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary"><?= icon('save', 18) ?> Enregistrer</button>
            </div>
        </div>
    </form>
</div>

<!-- ================================================================
     TAB: E-mails
     ================================================================ -->
<div class="settings-section <?= $currentTab === 'email' ? 'active' : '' ?>" id="tab-email">
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="email">

        <!-- SMTP -->
        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('send', 18) ?> Configuration SMTP</div>
                <div class="fields-grid">
                    <div class="form-group">
                        <label class="field-label" for="smtp_sender_name">Nom de l'expéditeur</label>
                        <input type="text" id="smtp_sender_name" name="smtp_sender_name" class="form-control"
                               value="<?= e(sv($settings, 'email', 'smtp_sender_name', 'Fête du Cidre')) ?>">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="smtp_sender_email">Email expéditeur</label>
                        <input type="email" id="smtp_sender_email" name="smtp_sender_email" class="form-control"
                               value="<?= e(sv($settings, 'email', 'smtp_sender_email')) ?>"
                               placeholder="noreply@fetecidre.fr">
                    </div>
                    <div class="form-group full">
                        <label class="field-label" for="smtp_reply_to">Email de réponse (Reply-To)</label>
                        <input type="email" id="smtp_reply_to" name="smtp_reply_to" class="form-control"
                               value="<?= e(sv($settings, 'email', 'smtp_reply_to')) ?>"
                               placeholder="contact@fetecidre.fr">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="smtp_host">Serveur SMTP</label>
                        <input type="text" id="smtp_host" name="smtp_host" class="form-control"
                               value="<?= e(sv($settings, 'email', 'smtp_host')) ?>"
                               placeholder="smtp.gmail.com">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="smtp_port">Port</label>
                        <input type="number" id="smtp_port" name="smtp_port" class="form-control"
                               value="<?= e(sv($settings, 'email', 'smtp_port', '587')) ?>">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="smtp_encryption">Chiffrement</label>
                        <select id="smtp_encryption" name="smtp_encryption" class="form-control">
                            <?php $enc = sv($settings, 'email', 'smtp_encryption', 'tls'); ?>
                            <option value="tls" <?= $enc === 'tls' ? 'selected' : '' ?>>TLS</option>
                            <option value="ssl" <?= $enc === 'ssl' ? 'selected' : '' ?>>SSL</option>
                            <option value="none" <?= $enc === 'none' ? 'selected' : '' ?>>Aucun</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="smtp_username">Identifiant SMTP</label>
                        <input type="text" id="smtp_username" name="smtp_username" class="form-control"
                               value="<?= e(sv($settings, 'email', 'smtp_username')) ?>">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="smtp_password">Mot de passe SMTP</label>
                        <input type="password" id="smtp_password" name="smtp_password" class="form-control"
                               value="<?= e(sv($settings, 'email', 'smtp_password')) ?>"
                               placeholder="••••••••">
                    </div>
                </div>
            </div>
        </div>

        <!-- Notifications -->
        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('bell', 18) ?> Notifications</div>
                <?php
                $notifs = [
                    ['key' => 'notif_new_order',     'label' => 'Nouvelle commande',       'desc' => 'Recevoir un email lors d\'une nouvelle commande'],
                    ['key' => 'notif_client_confirm', 'label' => 'Confirmation client',    'desc' => 'Envoyer un email de confirmation au client'],
                    ['key' => 'notif_contest_reg',   'label' => 'Inscription concours',    'desc' => 'Notification lors d\'une nouvelle inscription'],
                    ['key' => 'notif_weekly_report',  'label' => 'Rapport hebdomadaire',   'desc' => 'Recevoir un résumé chaque lundi matin'],
                ];
                foreach ($notifs as $n):
                    $val = sv($settings, 'email', $n['key'], '1');
                ?>
                    <div class="toggle-row">
                        <div class="toggle-info">
                            <div class="toggle-label"><?= e($n['label']) ?></div>
                            <div class="toggle-desc"><?= e($n['desc']) ?></div>
                        </div>
                        <div>
                            <input type="hidden" name="<?= $n['key'] ?>" value="0">
                            <button type="button" class="toggle-switch <?= $val === '1' ? 'active' : '' ?>"
                                    onclick="toggleSwitch(this, '<?= $n['key'] ?>')">
                                <span class="toggle-slider"></span>
                            </button>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary"><?= icon('save', 18) ?> Enregistrer</button>
            </div>
        </div>
    </form>
</div>

<!-- ================================================================
     TAB: Légal
     ================================================================ -->
<div class="settings-section <?= $currentTab === 'legal' ? 'active' : '' ?>" id="tab-legal">
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="legal">

        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('scale', 18) ?> Mentions légales</div>
                <div class="form-group">
                    <textarea id="legal_mentions" name="legal_mentions" class="form-control" rows="8"
                              placeholder="Raison sociale, siège social, directeur de publication..."><?= e(sv($settings, 'legal', 'legal_mentions')) ?></textarea>
                    <div class="field-hint">Contenu affiché sur la page Mentions légales</div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('file-code', 18) ?> Conditions Générales de Vente</div>
                <div class="form-group">
                    <textarea id="legal_cgv" name="legal_cgv" class="form-control" rows="8"
                              placeholder="Article 1 - Objet..."><?= e(sv($settings, 'legal', 'legal_cgv')) ?></textarea>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('shield', 18) ?> Politique de confidentialité</div>
                <div class="form-group">
                    <textarea id="legal_privacy" name="legal_privacy" class="form-control" rows="8"
                              placeholder="Collecte et traitement des données..."><?= e(sv($settings, 'legal', 'legal_privacy')) ?></textarea>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('cookie', 18) ?> Bandeau cookies</div>
                <div class="toggle-row" style="border-bottom:none;padding-bottom:0.5rem;">
                    <div class="toggle-info">
                        <div class="toggle-label">Activer le bandeau cookies</div>
                        <div class="toggle-desc">Affiche un bandeau de consentement aux visiteurs</div>
                    </div>
                    <div>
                        <input type="hidden" name="cookie_banner_enabled" value="0">
                        <button type="button" class="toggle-switch <?= sv($settings, 'legal', 'cookie_banner_enabled', '1') === '1' ? 'active' : '' ?>"
                                onclick="toggleSwitch(this, 'cookie_banner_enabled')">
                            <span class="toggle-slider"></span>
                        </button>
                    </div>
                </div>
                <div class="form-group" style="margin-top:0.75rem;">
                    <label class="field-label" for="cookie_banner_text">Texte du bandeau</label>
                    <textarea id="cookie_banner_text" name="cookie_banner_text" class="form-control" rows="3"
                              placeholder="Ce site utilise des cookies..."><?= e(sv($settings, 'legal', 'cookie_banner_text')) ?></textarea>
                </div>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary"><?= icon('save', 18) ?> Enregistrer</button>
            </div>
        </div>
    </form>
</div>

<!-- ================================================================
     TAB: Scripts
     ================================================================ -->
<div class="settings-section <?= $currentTab === 'scripts' ? 'active' : '' ?>" id="tab-scripts">
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="scripts">

        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('code', 18) ?> Injection de scripts personnalisés</div>
                <p style="font-size:0.8125rem;color:#888;margin-bottom:1.25rem;">
                    Ajoutez du code HTML, CSS ou JavaScript personnalisé dans les différentes zones de la page.
                </p>

                <!-- Head scripts -->
                <div class="script-block">
                    <div class="script-label">
                        Scripts &lt;head&gt;
                        <span class="tag">Avant &lt;/head&gt;</span>
                    </div>
                    <div class="script-editor">
                        <div class="script-editor-header">
                            <span>HTML / JS</span>
                        </div>
                        <textarea name="head_scripts" placeholder="<!-- Google Analytics, fonts, meta tags... -->"><?= e(sv($settings, 'scripts', 'head_scripts')) ?></textarea>
                        <div class="script-editor-hint">Ex : Google Fonts, analytics, meta tags personnalisées</div>
                    </div>
                </div>

                <!-- Body start scripts -->
                <div class="script-block">
                    <div class="script-label">
                        Scripts &lt;body&gt;
                        <span class="tag">Après &lt;body&gt;</span>
                    </div>
                    <div class="script-editor">
                        <div class="script-editor-header">
                            <span>HTML / JS</span>
                        </div>
                        <textarea name="body_start_scripts" placeholder="<!-- Google Tag Manager (noscript)... -->"><?= e(sv($settings, 'scripts', 'body_start_scripts')) ?></textarea>
                        <div class="script-editor-hint">Ex : Google Tag Manager (noscript), pixels de suivi</div>
                    </div>
                </div>

                <!-- Body end scripts -->
                <div class="script-block">
                    <div class="script-label">
                        Scripts &lt;/body&gt;
                        <span class="tag">Avant &lt;/body&gt;</span>
                    </div>
                    <div class="script-editor">
                        <div class="script-editor-header">
                            <span>HTML / JS</span>
                        </div>
                        <textarea name="body_end_scripts" placeholder="<!-- Widgets, chat, scripts tiers... -->"><?= e(sv($settings, 'scripts', 'body_end_scripts')) ?></textarea>
                        <div class="script-editor-hint">Ex : widgets, chat en ligne, scripts tiers</div>
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary"><?= icon('save', 18) ?> Enregistrer</button>
            </div>
        </div>
    </form>
</div>

<!-- ================================================================
     TAB: Avancé
     ================================================================ -->
<div class="settings-section <?= $currentTab === 'advanced' ? 'active' : '' ?>" id="tab-advanced">
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="advanced">

        <!-- Maintenance -->
        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('power', 18) ?> Mode maintenance</div>
                <?php if (sv($settings, 'advanced', 'maintenance_enabled') === '1'): ?>
                    <div class="maint-banner">
                        <?= icon('alert-triangle', 20) ?>
                        <div class="maint-banner-text">
                            <strong>Mode maintenance actif</strong>
                            Le site est actuellement inaccessible aux visiteurs.
                        </div>
                    </div>
                <?php endif; ?>
                <div class="toggle-row" style="border-bottom:none;">
                    <div class="toggle-info">
                        <div class="toggle-label">Activer le mode maintenance</div>
                        <div class="toggle-desc">Le site affichera une page de maintenance aux visiteurs</div>
                    </div>
                    <div>
                        <input type="hidden" name="maintenance_enabled" value="0">
                        <button type="button" class="toggle-switch <?= sv($settings, 'advanced', 'maintenance_enabled') === '1' ? 'active' : '' ?>"
                                onclick="toggleSwitch(this, 'maintenance_enabled')">
                            <span class="toggle-slider"></span>
                        </button>
                    </div>
                </div>
                <div class="form-group" style="margin-top:0.75rem;">
                    <label class="field-label" for="maintenance_message">Message de maintenance</label>
                    <textarea id="maintenance_message" name="maintenance_message" class="form-control" rows="3"
                              placeholder="Le site est en cours de maintenance. Nous serons de retour très bientôt !"><?= e(sv($settings, 'advanced', 'maintenance_message')) ?></textarea>
                </div>
            </div>
        </div>

        <!-- Analytics -->
        <div class="card">
            <div class="card-body">
                <div class="settings-card-title"><?= icon('bar-chart-3', 18) ?> Analytics</div>
                <div class="fields-grid">
                    <div class="form-group">
                        <label class="field-label" for="google_analytics">Google Analytics (GA4)</label>
                        <input type="text" id="google_analytics" name="google_analytics" class="form-control"
                               value="<?= e(sv($settings, 'advanced', 'google_analytics', sv($settings, 'seo', 'google_analytics'))) ?>"
                               placeholder="G-XXXXXXXXXX">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="matomo_url">URL Matomo</label>
                        <input type="url" id="matomo_url" name="matomo_url" class="form-control"
                               value="<?= e(sv($settings, 'advanced', 'matomo_url')) ?>"
                               placeholder="https://analytics.example.com">
                    </div>
                    <div class="form-group">
                        <label class="field-label" for="matomo_site_id">Site ID Matomo</label>
                        <input type="text" id="matomo_site_id" name="matomo_site_id" class="form-control"
                               value="<?= e(sv($settings, 'advanced', 'matomo_site_id')) ?>"
                               placeholder="1">
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary"><?= icon('save', 18) ?> Enregistrer</button>
            </div>
        </div>
    </form>

    <!-- Danger zone -->
    <div class="card">
        <div class="card-body">
            <div class="danger-zone">
                <h4><?= icon('alert-triangle', 16) ?> Zone dangereuse</h4>

                <div class="danger-item">
                    <div class="danger-item-info">
                        <div class="danger-item-title">Désactiver l'indexation</div>
                        <div class="danger-item-desc">Ajoute la balise noindex pour empêcher les moteurs de recherche</div>
                    </div>
                    <form method="post" action="/admin/settings" style="display:inline;">
                        <?= csrf_field() ?>
                        <input type="hidden" name="_tab" value="advanced">
                        <input type="hidden" name="noindex_enabled" value="<?= sv($settings, 'advanced', 'noindex_enabled') === '1' ? '0' : '1' ?>">
                        <button type="submit" class="btn btn-sm <?= sv($settings, 'advanced', 'noindex_enabled') === '1' ? 'btn-primary' : 'btn-danger' ?>">
                            <?= sv($settings, 'advanced', 'noindex_enabled') === '1' ? 'Réactiver' : 'Désactiver' ?>
                        </button>
                    </form>
                </div>

                <div class="danger-item">
                    <div class="danger-item-info">
                        <div class="danger-item-title">Vider le cache</div>
                        <div class="danger-item-desc">Supprime tous les fichiers en cache du site</div>
                    </div>
                    <form method="post" action="/admin/cache/clear" style="display:inline;">
                        <?= csrf_field() ?>
                        <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Vider tout le cache ?')">
                            <?= icon('trash-2', 14) ?> Vider
                        </button>
                    </form>
                </div>

                <div class="danger-item">
                    <div class="danger-item-info">
                        <div class="danger-item-title">Exporter la base de données</div>
                        <div class="danger-item-desc">Télécharge un dump SQL complet de la base</div>
                    </div>
                    <form method="post" action="/admin/settings/export-db" style="display:inline;">
                        <?= csrf_field() ?>
                        <button type="submit" class="btn btn-sm btn-secondary">
                            <?= icon('download', 14) ?> Exporter
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- ===== JavaScript ===== -->
<script>
function switchTab(tab) {
    // Update URL without reload
    const url = new URL(window.location);
    url.searchParams.set('tab', tab);
    history.pushState({}, '', url);

    // Hide all sections, show target
    document.querySelectorAll('.settings-section').forEach(s => s.classList.remove('active'));
    const target = document.getElementById('tab-' + tab);
    if (target) target.classList.add('active');

    // Update tabs
    document.querySelectorAll('.stab').forEach(t => t.classList.remove('active'));
    event.currentTarget.classList.add('active');
}

function toggleSwitch(btn, name) {
    btn.classList.toggle('active');
    const isActive = btn.classList.contains('active');
    const hiddenInput = btn.closest('form') ?
        btn.closest('form').querySelector('input[name="' + name + '"]') :
        btn.parentElement.querySelector('input[name="' + name + '"]');
    if (hiddenInput) {
        hiddenInput.value = isActive ? '1' : '0';
    }
}

// Handle back/forward navigation
window.addEventListener('popstate', function() {
    const url = new URL(window.location);
    const tab = url.searchParams.get('tab') || 'general';
    document.querySelectorAll('.settings-section').forEach(s => s.classList.remove('active'));
    const target = document.getElementById('tab-' + tab);
    if (target) target.classList.add('active');
    document.querySelectorAll('.stab').forEach(t => {
        t.classList.toggle('active', t.textContent.trim() === (<?= json_encode($tabs) ?>)[tab]);
    });
});
</script>
