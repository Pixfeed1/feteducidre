<?php
/**
 * Galerie photos — liste des albums groupés par année.
 * Variables : $grouped, $totalAlbums, $totalPhotos, $yearCount, $storageBytes, $typeLabels
 */

// Type icons & gradient classes
$typeIcons = [
    'fete'     => 'party-popper',
    'rallye'   => 'map',
    'affiches' => 'image',
    'general'  => 'calendar',
];

// Format storage size
$storageLabel = $storageBytes < 1048576
    ? round($storageBytes / 1024) . ' Ko'
    : ($storageBytes < 1073741824
        ? number_format($storageBytes / 1048576, 1, ',', '') . ' Mo'
        : number_format($storageBytes / 1073741824, 1, ',', '') . ' Go');
?>

<div style="max-width:1200px">

    <!-- PAGE HEADER -->
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-icon" style="background:var(--vert-mousse)"><?= icon('image', 22, '', 'white') ?></div>
            <h1>Galerie photos</h1>
        </div>
        <div class="page-header-actions">
            <a href="/admin/albums/create" class="btn btn-primary">
                <?= icon('plus', 15) ?> Nouvel album
            </a>
        </div>
    </div>

    <!-- STATS -->
    <div class="stats-row">
        <div class="gal-stat">
            <div class="gal-stat-icon" style="background:rgba(74,107,62,0.12)"><?= icon('folder-open', 20, '', 'var(--vert-mousse)') ?></div>
            <div><div class="gal-stat-value"><?= $totalAlbums ?></div><div class="gal-stat-label">Albums</div></div>
        </div>
        <div class="gal-stat">
            <div class="gal-stat-icon" style="background:rgba(212,131,59,0.12)"><?= icon('image', 20, '', 'var(--orange-cidre)') ?></div>
            <div><div class="gal-stat-value"><?= $totalPhotos ?></div><div class="gal-stat-label">Photos</div></div>
        </div>
        <div class="gal-stat">
            <div class="gal-stat-icon" style="background:rgba(92,61,46,0.12)"><?= icon('calendar', 20, '', 'var(--brun)') ?></div>
            <div><div class="gal-stat-value"><?= $yearCount ?></div><div class="gal-stat-label">Années</div></div>
        </div>
        <div class="gal-stat">
            <div class="gal-stat-icon" style="background:rgba(59,130,246,0.12)"><?= icon('hard-drive', 20, '', '#3B82F6') ?></div>
            <div><div class="gal-stat-value"><?= $storageLabel ?></div><div class="gal-stat-label">Espace utilisé</div></div>
        </div>
    </div>

    <!-- TOOLBAR -->
    <div class="toolbar">
        <div class="search-box">
            <span class="search-icon"><?= icon('search', 15) ?></span>
            <input type="text" placeholder="Rechercher un album…" id="albumSearch">
        </div>
        <div class="filter-chips">
            <button class="chip active" data-filter="all">Tout</button>
            <button class="chip" data-filter="fete"><?= icon('party-popper', 11) ?> Fête</button>
            <button class="chip" data-filter="rallye"><?= icon('map', 11) ?> Rallye</button>
            <button class="chip" data-filter="affiches"><?= icon('image', 11) ?> Affiches</button>
            <button class="chip" data-filter="general"><?= icon('calendar', 11) ?> Général</button>
        </div>
    </div>

    <!-- YEAR GROUPS -->
    <?php if (empty($grouped)): ?>
        <div class="card">
            <div class="card-body">
                <div class="empty-state" style="text-align:center;padding:3rem">
                    <?= icon('images', 40) ?>
                    <p style="margin-top:0.8rem;color:var(--texte-leger)">Aucun album pour le moment.</p>
                    <a href="/admin/albums/create" class="btn btn-primary" style="margin-top:1rem"><?= icon('plus', 15) ?> Créer un album</a>
                </div>
            </div>
        </div>
    <?php else: ?>
        <?php foreach ($grouped as $year => $yearAlbums): ?>
            <?php
                $yearLabel = $year ?: 'Sans année';
                $photoSum = array_sum(array_column($yearAlbums, 'photo_count'));
                $albumCount = count($yearAlbums);
            ?>
            <div class="year-group" data-year="<?= (int) $year ?>">
                <div class="year-header">
                    <span class="year-label"><?= e((string) $yearLabel) ?></span>
                    <div class="year-line"></div>
                    <span class="year-count"><?= $albumCount ?> album<?= $albumCount > 1 ? 's' : '' ?> · <?= $photoSum ?> photo<?= $photoSum > 1 ? 's' : '' ?></span>
                </div>

                <div class="albums-grid">
                    <?php foreach ($yearAlbums as $album): ?>
                        <?php
                            $type = $album['type'] ?? 'fete';
                            $typeLabel = $typeLabels[$type] ?? 'Fête';
                            $typeIcon = $typeIcons[$type] ?? 'party-popper';
                            $photoCount = (int) $album['photo_count'];
                            $isActive = (bool) $album['is_active'];
                        ?>
                        <div class="album-card" data-type="<?= e($type) ?>" data-title="<?= e(mb_strtolower($album['title'])) ?>">
                            <a href="/admin/albums/<?= (int) $album['id'] ?>/edit" style="text-decoration:none;color:inherit;display:block">
                                <div class="album-cover">
                                    <div class="album-cover-bg <?= e($type) ?>"></div>
                                    <div class="album-cover-overlay"></div>
                                    <div class="album-cover-badges">
                                        <span class="type-badge"><?= icon($typeIcon, 10, '', 'currentColor') ?> <?= e($typeLabel) ?></span>
                                        <span class="count-badge"><?= icon('image', 10, '', 'currentColor') ?> <?= $photoCount ?></span>
                                    </div>
                                    <div class="album-cover-title">
                                        <h3><?= e($album['title']) ?></h3>
                                        <?php if (!empty($album['description'])): ?>
                                            <span><?= e(mb_strimwidth($album['description'], 0, 40, '…')) ?></span>
                                        <?php endif; ?>
                                    </div>
                                </div>
                            </a>
                            <div class="album-info">
                                <div class="album-meta">
                                    <?php if ($isActive): ?>
                                        <span class="album-status published"><?= icon('circle', 7, '', 'currentColor') ?> Publié</span>
                                    <?php else: ?>
                                        <span class="album-status draft"><?= icon('circle', 7, '', 'currentColor') ?> Brouillon</span>
                                    <?php endif; ?>
                                </div>
                                <div class="album-actions">
                                    <a href="/admin/albums/<?= (int) $album['id'] ?>/edit" class="btn-icon" title="Modifier"><?= icon('pencil', 13) ?></a>
                                    <form method="post" action="/admin/albums/<?= (int) $album['id'] ?>/delete"
                                          style="display:inline" onsubmit="return confirm('Supprimer cet album et toutes ses photos ?')">
                                        <?= csrf_field() ?>
                                        <button type="submit" class="btn-icon" title="Supprimer" style="color:var(--rouge)"><?= icon('trash-2', 13) ?></button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>

                    <a href="/admin/albums/create?year=<?= (int) $year ?>" class="add-album-card">
                        <div class="add-album-icon"><?= icon('plus', 20) ?></div>
                        <span>Ajouter un album</span>
                    </a>
                </div>
            </div>
        <?php endforeach; ?>
    <?php endif; ?>

</div>

<script>
(function() {
    // Filter by type
    var chips = document.querySelectorAll('.chip[data-filter]');
    chips.forEach(function(chip) {
        chip.addEventListener('click', function() {
            chips.forEach(function(c) { c.classList.remove('active'); });
            this.classList.add('active');
            var type = this.dataset.filter;
            document.querySelectorAll('.album-card').forEach(function(card) {
                card.style.display = (type === 'all' || card.dataset.type === type) ? '' : 'none';
            });
            // Hide empty year groups
            document.querySelectorAll('.year-group').forEach(function(group) {
                var visible = group.querySelectorAll('.album-card:not([style*="display: none"])');
                group.style.display = visible.length === 0 ? 'none' : '';
            });
        });
    });

    // Search
    var searchInput = document.getElementById('albumSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            var q = this.value.toLowerCase().trim();
            document.querySelectorAll('.album-card').forEach(function(card) {
                var title = card.dataset.title || '';
                card.style.display = (!q || title.includes(q)) ? '' : 'none';
            });
            document.querySelectorAll('.year-group').forEach(function(group) {
                var visible = group.querySelectorAll('.album-card:not([style*="display: none"])');
                group.style.display = visible.length === 0 ? 'none' : '';
            });
        });
    }
})();
</script>
