<?php
/**
 * Formulaire de création/modification d'une page.
 * Variables : $page (null si création)
 */

$isEdit = $page !== null;
$action = $isEdit ? '/admin/pages/' . (int) $page['id'] . '/update' : '/admin/pages/store';
?>

<div class="page-header">
    <h1><?= $isEdit ? icon('edit', 24) . ' Modifier la page' : icon('plus', 24) . ' Nouvelle page' ?></h1>
    <a href="/admin/pages" class="btn btn-secondary">
        <?= icon('arrow-left', 18) ?> Retour
    </a>
</div>

<form method="post" action="<?= $action ?>">
    <?= csrf_field() ?>

    <div class="card">
        <div class="card-body">
            <div class="form-row">
                <div class="form-group">
                    <label for="title">Titre *</label>
                    <input type="text" id="title" name="title" class="form-control"
                           value="<?= e($isEdit ? $page['title'] : old('title')) ?>"
                           required>
                </div>
                <div class="form-group">
                    <label for="slug">Slug (URL)</label>
                    <input type="text" id="slug" name="slug" class="form-control"
                           value="<?= e($isEdit ? $page['slug'] : old('slug')) ?>"
                           placeholder="Généré automatiquement si vide">
                    <div class="form-hint">Laissez vide pour générer automatiquement depuis le titre.</div>
                </div>
            </div>

            <div class="form-group">
                <label for="content">Contenu</label>
                <textarea id="content" name="content" class="form-control" rows="15"><?= e($isEdit ? $page['content'] : old('content')) ?></textarea>
            </div>

            <div class="form-group">
                <label for="excerpt">Extrait</label>
                <textarea id="excerpt" name="excerpt" class="form-control" rows="3"><?= e($isEdit ? ($page['excerpt'] ?? '') : old('excerpt')) ?></textarea>
                <div class="form-hint">Court résumé affiché dans les aperçus.</div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="template">Template</label>
                    <select id="template" name="template" class="form-control">
                        <?php
                        $templates = ['default' => 'Par défaut', 'home' => 'Accueil', 'page' => 'Page standard', 'shop' => 'Boutique', 'gallery' => 'Galerie', 'archive' => 'Archives', 'contest' => 'Concours', 'hike' => 'Randonnée', 'contact' => 'Contact', 'legal' => 'Mentions légales'];
                        $currentTemplate = $isEdit ? $page['template'] : old('template', 'default');
                        foreach ($templates as $value => $label):
                        ?>
                            <option value="<?= $value ?>" <?= $currentTemplate === $value ? 'selected' : '' ?>>
                                <?= e($label) ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="form-group">
                    <label for="status">Statut</label>
                    <select id="status" name="status" class="form-control">
                        <?php $currentStatus = $isEdit ? $page['status'] : old('status', 'draft'); ?>
                        <option value="draft" <?= $currentStatus === 'draft' ? 'selected' : '' ?>>Brouillon</option>
                        <option value="published" <?= $currentStatus === 'published' ? 'selected' : '' ?>>Publiée</option>
                    </select>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <div class="form-check">
                        <input type="checkbox" id="in_menu" name="in_menu" value="1"
                               <?= ($isEdit ? $page['in_menu'] : old('in_menu')) ? 'checked' : '' ?>>
                        <label for="in_menu">Afficher dans le menu de navigation</label>
                    </div>
                </div>
                <div class="form-group">
                    <label for="menu_order">Ordre dans le menu</label>
                    <input type="number" id="menu_order" name="menu_order" class="form-control"
                           value="<?= e($isEdit ? (string) $page['menu_order'] : old('menu_order', '0')) ?>" min="0">
                </div>
            </div>
        </div>
    </div>

    <!-- SEO -->
    <div class="card">
        <div class="card-header">
            <h2><?= icon('search', 20) ?> Référencement (SEO)</h2>
        </div>
        <div class="card-body">
            <div class="form-group">
                <label for="meta_title">Meta titre</label>
                <input type="text" id="meta_title" name="meta_title" class="form-control"
                       value="<?= e($isEdit ? ($page['meta_title'] ?? '') : old('meta_title')) ?>"
                       maxlength="70">
                <div class="form-hint">Laissez vide pour utiliser le titre de la page. 70 caractères max.</div>
            </div>
            <div class="form-group">
                <label for="meta_description">Meta description</label>
                <textarea id="meta_description" name="meta_description" class="form-control" rows="2"
                          maxlength="160"><?= e($isEdit ? ($page['meta_description'] ?? '') : old('meta_description')) ?></textarea>
                <div class="form-hint">160 caractères max.</div>
            </div>
        </div>
    </div>

    <div class="card-footer" style="background:none; border:none; padding: 0; margin-top: 1rem;">
        <a href="/admin/pages" class="btn btn-secondary">Annuler</a>
        <button type="submit" class="btn btn-primary">
            <?= icon('save', 18) ?> <?= $isEdit ? 'Mettre à jour' : 'Créer la page' ?>
        </button>
    </div>
</form>
