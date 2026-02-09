<?php
/**
 * Template page d'accueil.
 * Variables : $page, $seo, $settings, $featuredProducts, $editions, $partners
 */

$eventDate = $settings['general']['next_event_date'] ?? '';
$eventTime = $settings['general']['next_event_time'] ?? '';
$siteName = $settings['general']['site_name'] ?? 'Fête du Cidre';
?>

<!-- Hero Section -->
<section class="hero">
    <div class="hero-overlay"></div>
    <div class="container hero-content">
        <span class="hero-badge"><?= icon('apple', 18) ?> Association loi 1901 — Depuis 1989</span>
        <h1 class="hero-title"><?= e($siteName) ?></h1>
        <p class="hero-subtitle">L'Hôtellerie de Flée, Maine-et-Loire (49)</p>

        <?php if ($eventDate): ?>
        <div class="hero-event">
            <div class="hero-date">
                <?= icon('calendar', 20) ?>
                <span>Prochaine édition : <strong><?= date_fr($eventDate) ?></strong></span>
            </div>
            <?php if ($eventTime): ?>
            <div class="hero-time">
                <?= icon('clock', 18) ?>
                <span><?= e($eventTime) ?></span>
            </div>
            <?php endif; ?>
        </div>
        <?php endif; ?>

        <div class="hero-actions">
            <a href="/infos-pratiques" class="btn btn-secondary">
                <?= icon('info', 18) ?> Infos Pratiques
            </a>
            <a href="/boutique" class="btn btn-outline" style="border-color:#fff;color:#fff">
                <?= icon('shopping-bag', 18) ?> Boutique en ligne
            </a>
        </div>
    </div>
</section>

<!-- Section Présentation -->
<section class="section section-about">
    <div class="container">
        <div class="section-title">
            <h2>Bienvenue à la Fête du Cidre</h2>
            <p>Une tradition vivante au cœur du Maine-et-Loire</p>
        </div>

        <div class="about-grid grid grid-3">
            <div class="about-card card">
                <div class="card-body">
                    <div class="about-icon"><?= icon('apple', 32, '', 'var(--vert-profond)') ?></div>
                    <h3>Tradition Cidricole</h3>
                    <p>Découvrez les secrets de fabrication du cidre artisanal, un savoir-faire transmis de génération en génération.</p>
                </div>
            </div>
            <div class="about-card card">
                <div class="card-body">
                    <div class="about-icon"><?= icon('trophy', 32, '', 'var(--vert-profond)') ?></div>
                    <h3>Concours de Cidre</h3>
                    <p>Le concours réunit les meilleurs producteurs de la région pour élire les cidres d'exception.</p>
                </div>
            </div>
            <div class="about-card card">
                <div class="card-body">
                    <div class="about-icon"><?= icon('users', 32, '', 'var(--vert-profond)') ?></div>
                    <h3>Convivialité</h3>
                    <p>Un événement festif et familial : animations, dégustations, marché du terroir et randonnée.</p>
                </div>
            </div>
        </div>

        <div class="about-cta" style="text-align:center;margin-top:2rem">
            <a href="/origines" class="btn btn-primary">
                Découvrir nos origines <?= icon('arrow-right', 18) ?>
            </a>
        </div>
    </div>
</section>

<!-- Section Produits -->
<?php if (!empty($featuredProducts)): ?>
<section class="section section-products" style="background:var(--blanc)">
    <div class="container">
        <div class="section-title">
            <h2>Notre Boutique</h2>
            <p>Cidres, jus de pomme et produits du terroir</p>
        </div>

        <div class="grid grid-3">
            <?php foreach ($featuredProducts as $product): ?>
            <div class="card product-card">
                <div class="product-image" style="background:var(--creme-fonce);height:200px;display:flex;align-items:center;justify-content:center">
                    <?= icon('wine', 48, '', 'var(--vert-clair)') ?>
                </div>
                <div class="card-body">
                    <?php if ($product['category']): ?>
                        <span class="product-category"><?= e(ucfirst($product['category'])) ?></span>
                    <?php endif; ?>
                    <h3 class="product-name"><?= e($product['name']) ?></h3>
                    <p class="product-desc"><?= e(truncate($product['short_description'] ?? '', 100)) ?></p>
                    <div class="product-footer">
                        <span class="product-price"><?= number_format((float)$product['price'], 2, ',', ' ') ?> €</span>
                        <?php if ($product['volume']): ?>
                            <span class="product-volume"><?= e($product['volume']) ?></span>
                        <?php endif; ?>
                    </div>
                    <a href="/boutique/<?= e($product['slug']) ?>" class="btn btn-primary btn-sm" style="margin-top:.75rem;width:100%;justify-content:center">
                        Voir le produit
                    </a>
                </div>
            </div>
            <?php endforeach; ?>
        </div>

        <div style="text-align:center;margin-top:2rem">
            <a href="/boutique" class="btn btn-outline">
                Voir toute la boutique <?= icon('arrow-right', 18) ?>
            </a>
        </div>
    </div>
</section>
<?php endif; ?>

<!-- Section Éditions -->
<?php if (!empty($editions)): ?>
<section class="section section-editions">
    <div class="container">
        <div class="section-title">
            <h2>Les Éditions Passées</h2>
            <p>Depuis 1989, la Fête du Cidre écrit son histoire</p>
        </div>

        <div class="grid grid-4">
            <?php foreach ($editions as $edition): ?>
            <a href="/archives/<?= $edition['year'] ?>" class="card edition-card">
                <div class="card-body" style="text-align:center;padding:2rem">
                    <span class="edition-year"><?= $edition['year'] ?></span>
                    <h3><?= e($edition['title'] ?? 'Édition ' . $edition['year']) ?></h3>
                    <span class="btn-link" style="color:var(--orange-cidre);font-weight:600">
                        Découvrir <?= icon('arrow-right', 16) ?>
                    </span>
                </div>
            </a>
            <?php endforeach; ?>
        </div>

        <div style="text-align:center;margin-top:2rem">
            <a href="/archives" class="btn btn-outline">
                Toutes les archives <?= icon('arrow-right', 18) ?>
            </a>
        </div>
    </div>
</section>
<?php endif; ?>

<!-- Section Partenaires -->
<?php if (!empty($partners)): ?>
<section class="section section-partners" style="background:var(--blanc)">
    <div class="container">
        <div class="section-title">
            <h2>Nos Partenaires</h2>
            <p>Merci à tous ceux qui rendent cet événement possible</p>
        </div>

        <div class="partners-grid">
            <?php foreach ($partners as $partner): ?>
            <div class="partner-item">
                <span class="partner-name"><?= e($partner['name']) ?></span>
            </div>
            <?php endforeach; ?>
        </div>
    </div>
</section>
<?php endif; ?>
