<?php
/**
 * Formulaire de création/modification d'un album avec zone d'upload de photos.
 * Variables : $album (null si création), $photos
 */

$isEdit = $album !== null;
$action = $isEdit ? '/admin/albums/' . (int) $album['id'] . '/update' : '/admin/albums/store';
$photos = $photos ?? [];
?>

<div class="page-header">
    <h1><?= $isEdit ? icon('edit', 24) . ' Modifier l\'album' : icon('plus', 24) . ' Nouvel album' ?></h1>
    <a href="/admin/albums" class="btn btn-secondary">
        <?= icon('arrow-left', 18) ?> Retour
    </a>
</div>

<form method="post" action="<?= $action ?>">
    <?= csrf_field() ?>

    <div class="card">
        <div class="card-header">
            <h2>Informations de l'album</h2>
        </div>
        <div class="card-body">
            <div class="form-row">
                <div class="form-group">
                    <label for="title">Titre *</label>
                    <input type="text" id="title" name="title" class="form-control"
                           value="<?= e($isEdit ? $album['title'] : old('title')) ?>"
                           required>
                </div>
                <div class="form-group">
                    <label for="slug">Slug</label>
                    <input type="text" id="slug" name="slug" class="form-control"
                           value="<?= e($isEdit ? $album['slug'] : old('slug')) ?>"
                           placeholder="Généré automatiquement">
                </div>
            </div>

            <div class="form-group">
                <label for="description">Description</label>
                <textarea id="description" name="description" class="form-control" rows="3"><?= e($isEdit ? ($album['description'] ?? '') : old('description')) ?></textarea>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="year">Année</label>
                    <input type="number" id="year" name="year" class="form-control"
                           value="<?= e($isEdit ? (string) ($album['year'] ?? '') : old('year')) ?>"
                           min="1989" max="<?= date('Y') + 1 ?>">
                </div>
                <div class="form-group">
                    <label for="sort_order">Ordre d'affichage</label>
                    <input type="number" id="sort_order" name="sort_order" class="form-control"
                           value="<?= e($isEdit ? (string) $album['sort_order'] : old('sort_order', '0')) ?>" min="0">
                </div>
                <div class="form-group">
                    <div class="form-check" style="margin-top: 1.75rem;">
                        <input type="checkbox" id="is_active" name="is_active" value="1"
                               <?= ($isEdit ? $album['is_active'] : old('is_active', '1')) ? 'checked' : '' ?>>
                        <label for="is_active">Album actif (visible sur le site)</label>
                    </div>
                </div>
            </div>
        </div>
        <div class="card-footer">
            <a href="/admin/albums" class="btn btn-secondary">Annuler</a>
            <button type="submit" class="btn btn-primary">
                <?= icon('save', 18) ?> <?= $isEdit ? 'Mettre à jour' : 'Créer l\'album' ?>
            </button>
        </div>
    </div>
</form>

<?php if ($isEdit): ?>
    <!-- Zone d'upload de photos -->
    <div class="card">
        <div class="card-header">
            <h2><?= icon('upload', 20) ?> Ajouter des photos</h2>
        </div>
        <div class="card-body">
            <form method="post" action="/admin/albums/<?= (int) $album['id'] ?>/photos" enctype="multipart/form-data">
                <?= csrf_field() ?>
                <div class="upload-zone" onclick="document.getElementById('photoInput').click()">
                    <div class="upload-icon"><?= icon('upload', 40) ?></div>
                    <p>Cliquez ou glissez-déposez vos photos ici</p>
                    <p class="text-muted" style="font-size:0.75rem;">JPG, PNG, WebP — Plusieurs fichiers autorisés</p>
                    <input type="file" id="photoInput" name="photos[]" multiple accept="image/*"
                           style="display:none" onchange="this.form.submit()">
                </div>
            </form>
        </div>
    </div>

    <!-- Photos existantes -->
    <?php if (!empty($photos)): ?>
        <div class="card">
            <div class="card-header">
                <h2><?= icon('image', 20) ?> Photos (<?= count($photos) ?>)</h2>
            </div>
            <div class="card-body">
                <div class="photo-grid">
                    <?php foreach ($photos as $photo): ?>
                        <div class="photo-item">
                            <img src="/storage/uploads/large/<?= e($photo['filename']) ?>"
                                 alt="<?= e($photo['title'] ?? $photo['original_name']) ?>"
                                 loading="lazy">
                            <div class="photo-actions">
                                <form method="post" action="/admin/photos/<?= (int) $photo['id'] ?>/delete"
                                      onsubmit="return confirm('Supprimer cette photo ?')">
                                    <?= csrf_field() ?>
                                    <button type="submit" class="btn btn-sm btn-danger" title="Supprimer">
                                        <?= icon('trash-2', 14) ?>
                                    </button>
                                </form>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>
    <?php endif; ?>
<?php endif; ?>
