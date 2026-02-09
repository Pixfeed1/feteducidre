<?php
/**
 * Formulaire des paramètres avec onglets — administration.
 * Variables : $settings, $currentTab, $defaultColors
 */

$tabs = [
    'general' => 'Général',
    'social'  => 'Réseaux sociaux',
    'shop'    => 'Boutique',
    'colors'  => 'Couleurs',
    'scripts' => 'Scripts',
    'seo'     => 'SEO',
];

/** Récupère la valeur d'un paramètre */
function setting_value(array $settings, string $group, string $key, string $default = ''): string
{
    return $settings[$group][$key]['value'] ?? $default;
}

/** Récupère le label d'un paramètre */
function setting_label(array $settings, string $group, string $key, string $default = ''): string
{
    return $settings[$group][$key]['label'] ?? $default;
}
?>

<div class="page-header">
    <h1><?= icon('settings', 24) ?> Paramètres</h1>
    <div class="actions">
        <form method="post" action="/admin/cache/clear" style="display:inline;">
            <?= csrf_field() ?>
            <button type="submit" class="btn btn-secondary" onclick="return confirm('Vider tout le cache ?')">
                <?= icon('refresh-cw', 18) ?> Vider le cache
            </button>
        </form>
    </div>
</div>

<!-- Onglets -->
<div class="tabs">
    <?php foreach ($tabs as $key => $label): ?>
        <a href="/admin/settings?tab=<?= $key ?>" class="tab-link <?= $currentTab === $key ? 'active' : '' ?>">
            <?= $label ?>
        </a>
    <?php endforeach; ?>
</div>

<!-- Onglet Général -->
<?php if ($currentTab === 'general'): ?>
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="general">

        <div class="card">
            <div class="card-body">
                <div class="form-group">
                    <label for="site_name"><?= setting_label($settings, 'general', 'site_name', 'Nom du site') ?></label>
                    <input type="text" id="site_name" name="site_name" class="form-control"
                           value="<?= e(setting_value($settings, 'general', 'site_name', 'Fête du Cidre')) ?>">
                </div>
                <div class="form-group">
                    <label for="site_description"><?= setting_label($settings, 'general', 'site_description', 'Description du site') ?></label>
                    <input type="text" id="site_description" name="site_description" class="form-control"
                           value="<?= e(setting_value($settings, 'general', 'site_description')) ?>">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="association_name">Nom de l'association</label>
                        <input type="text" id="association_name" name="association_name" class="form-control"
                               value="<?= e(setting_value($settings, 'general', 'association_name')) ?>">
                    </div>
                    <div class="form-group">
                        <label for="association_email">Email de contact</label>
                        <input type="email" id="association_email" name="association_email" class="form-control"
                               value="<?= e(setting_value($settings, 'general', 'association_email')) ?>">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="association_phone">Téléphone</label>
                        <input type="text" id="association_phone" name="association_phone" class="form-control"
                               value="<?= e(setting_value($settings, 'general', 'association_phone')) ?>">
                    </div>
                    <div class="form-group">
                        <label for="association_address">Adresse</label>
                        <input type="text" id="association_address" name="association_address" class="form-control"
                               value="<?= e(setting_value($settings, 'general', 'association_address')) ?>">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="next_event_date">Date du prochain événement</label>
                        <input type="date" id="next_event_date" name="next_event_date" class="form-control"
                               value="<?= e(setting_value($settings, 'general', 'next_event_date')) ?>">
                    </div>
                    <div class="form-group">
                        <label for="next_event_time">Horaires</label>
                        <input type="text" id="next_event_time" name="next_event_time" class="form-control"
                               value="<?= e(setting_value($settings, 'general', 'next_event_time')) ?>">
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary">
                    <?= icon('save', 18) ?> Enregistrer
                </button>
            </div>
        </div>
    </form>
<?php endif; ?>

<!-- Onglet Réseaux sociaux -->
<?php if ($currentTab === 'social'): ?>
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="social">

        <div class="card">
            <div class="card-body">
                <div class="form-group">
                    <label for="facebook_url"><?= icon('facebook', 18) ?> Page Facebook</label>
                    <input type="url" id="facebook_url" name="facebook_url" class="form-control"
                           value="<?= e(setting_value($settings, 'social', 'facebook_url')) ?>"
                           placeholder="https://facebook.com/...">
                </div>
                <div class="form-group">
                    <label for="instagram_url"><?= icon('instagram', 18) ?> Compte Instagram</label>
                    <input type="url" id="instagram_url" name="instagram_url" class="form-control"
                           value="<?= e(setting_value($settings, 'social', 'instagram_url')) ?>"
                           placeholder="https://instagram.com/...">
                </div>
                <div class="form-group">
                    <label for="youtube_url"><?= icon('youtube', 18) ?> Chaîne YouTube</label>
                    <input type="url" id="youtube_url" name="youtube_url" class="form-control"
                           value="<?= e(setting_value($settings, 'social', 'youtube_url')) ?>"
                           placeholder="https://youtube.com/...">
                </div>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary">
                    <?= icon('save', 18) ?> Enregistrer
                </button>
            </div>
        </div>
    </form>
<?php endif; ?>

<!-- Onglet Boutique -->
<?php if ($currentTab === 'shop'): ?>
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="shop">

        <div class="card">
            <div class="card-body">
                <div class="form-group">
                    <div class="form-check">
                        <input type="hidden" name="shop_enabled" value="0">
                        <input type="checkbox" id="shop_enabled" name="shop_enabled" value="1"
                               <?= setting_value($settings, 'shop', 'shop_enabled', '1') === '1' ? 'checked' : '' ?>>
                        <label for="shop_enabled">Boutique en ligne activée</label>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="shipping_cost">Frais de port (&euro;)</label>
                        <input type="number" id="shipping_cost" name="shipping_cost" class="form-control"
                               value="<?= e(setting_value($settings, 'shop', 'shipping_cost', '5.90')) ?>"
                               step="0.01" min="0">
                    </div>
                    <div class="form-group">
                        <label for="free_shipping_threshold">Franco de port (&euro;)</label>
                        <input type="number" id="free_shipping_threshold" name="free_shipping_threshold" class="form-control"
                               value="<?= e(setting_value($settings, 'shop', 'free_shipping_threshold', '50.00')) ?>"
                               step="0.01" min="0">
                        <div class="form-hint">Montant à partir duquel la livraison est gratuite.</div>
                    </div>
                    <div class="form-group">
                        <label for="tax_rate">Taux de TVA (%)</label>
                        <input type="number" id="tax_rate" name="tax_rate" class="form-control"
                               value="<?= e(setting_value($settings, 'shop', 'tax_rate', '20')) ?>"
                               step="0.1" min="0">
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary">
                    <?= icon('save', 18) ?> Enregistrer
                </button>
            </div>
        </div>
    </form>
<?php endif; ?>

<!-- Onglet Couleurs -->
<?php if ($currentTab === 'colors'): ?>
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="colors">

        <div class="card">
            <div class="card-header">
                <h2>Charte graphique</h2>
                <form method="post" action="/admin/settings/colors/reset" style="display:inline;">
                    <?= csrf_field() ?>
                    <button type="submit" class="btn btn-sm btn-secondary"
                            onclick="return confirm('Réinitialiser toutes les couleurs aux valeurs par défaut ?')">
                        <?= icon('refresh-cw', 16) ?> Réinitialiser
                    </button>
                </form>
            </div>
            <div class="card-body">
                <div class="color-group">
                    <?php
                    $colorSettings = $settings['colors'] ?? [];
                    foreach ($defaultColors as $name => $defaultHex):
                        $currentHex = $colorSettings[$name]['value'] ?? $defaultHex;
                        $label = $colorSettings[$name]['label'] ?? ucfirst(str_replace('-', ' ', $name));
                    ?>
                        <div class="color-field">
                            <input type="color" id="color_<?= $name ?>" name="<?= e($name) ?>"
                                   value="<?= e($currentHex) ?>">
                            <div>
                                <label for="color_<?= $name ?>" style="margin:0;"><?= e($label) ?></label>
                                <div class="form-hint"><?= e($currentHex) ?> (défaut : <?= e($defaultHex) ?>)</div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary">
                    <?= icon('save', 18) ?> Enregistrer les couleurs
                </button>
            </div>
        </div>
    </form>
<?php endif; ?>

<!-- Onglet Scripts -->
<?php if ($currentTab === 'scripts'): ?>
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="scripts">

        <div class="card">
            <div class="card-body">
                <div class="form-group">
                    <label for="head_scripts">Scripts dans le &lt;head&gt;</label>
                    <textarea id="head_scripts" name="head_scripts" class="form-control" rows="5"
                              style="font-family:monospace;font-size:0.8125rem;"><?= e(setting_value($settings, 'scripts', 'head_scripts')) ?></textarea>
                    <div class="form-hint">Code injecté juste avant &lt;/head&gt;. Ex : Google Fonts, analytics.</div>
                </div>
                <div class="form-group">
                    <label for="body_start_scripts">Scripts après &lt;body&gt;</label>
                    <textarea id="body_start_scripts" name="body_start_scripts" class="form-control" rows="5"
                              style="font-family:monospace;font-size:0.8125rem;"><?= e(setting_value($settings, 'scripts', 'body_start_scripts')) ?></textarea>
                    <div class="form-hint">Code injecté juste après &lt;body&gt;. Ex : Google Tag Manager (noscript).</div>
                </div>
                <div class="form-group">
                    <label for="body_end_scripts">Scripts avant &lt;/body&gt;</label>
                    <textarea id="body_end_scripts" name="body_end_scripts" class="form-control" rows="5"
                              style="font-family:monospace;font-size:0.8125rem;"><?= e(setting_value($settings, 'scripts', 'body_end_scripts')) ?></textarea>
                    <div class="form-hint">Code injecté juste avant &lt;/body&gt;. Ex : widgets, chat.</div>
                </div>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary">
                    <?= icon('save', 18) ?> Enregistrer
                </button>
            </div>
        </div>
    </form>
<?php endif; ?>

<!-- Onglet SEO -->
<?php if ($currentTab === 'seo'): ?>
    <form method="post" action="/admin/settings">
        <?= csrf_field() ?>
        <input type="hidden" name="_tab" value="seo">

        <div class="card">
            <div class="card-body">
                <div class="form-group">
                    <label for="google_analytics">ID Google Analytics</label>
                    <input type="text" id="google_analytics" name="google_analytics" class="form-control"
                           value="<?= e(setting_value($settings, 'seo', 'google_analytics')) ?>"
                           placeholder="G-XXXXXXXXXX">
                </div>
                <div class="form-group">
                    <label for="google_tag_manager">ID Google Tag Manager</label>
                    <input type="text" id="google_tag_manager" name="google_tag_manager" class="form-control"
                           value="<?= e(setting_value($settings, 'seo', 'google_tag_manager')) ?>"
                           placeholder="GTM-XXXXXXX">
                </div>
            </div>
            <div class="card-footer">
                <button type="submit" class="btn btn-primary">
                    <?= icon('save', 18) ?> Enregistrer
                </button>
            </div>
        </div>
    </form>
<?php endif; ?>
