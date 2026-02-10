<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur pour la gestion des partenaires et catégories.
 */
class PartnerAdminController extends Controller
{
    /** Couleurs disponibles pour les catégories */
    private const COLORS = [
        '#3B82F6', '#2C4A2E', '#D4833B', '#5C3D2E',
        '#7A9E6B', '#8B5CF6', '#EC4899',
    ];

    /** Icônes disponibles pour les catégories */
    private const ICONS = [
        'radio'         => 'Médias',
        'landmark'      => 'Finance',
        'building'      => 'Institutions',
        'briefcase'     => 'Services',
        'apple'         => 'Local',
        'target'        => 'Sponsors',
        'award'         => 'Mécènes',
        'handshake'     => 'Associations',
        'shopping-cart'  => 'Commerce',
    ];

    /**
     * Page principale : liste des partenaires groupés par catégorie
     */
    public function index(Request $request, array $params = []): void
    {
        $categories = $this->db()->fetchAll(
            "SELECT * FROM partner_categories ORDER BY sort_order ASC, name ASC"
        );

        $partners = $this->db()->fetchAll(
            "SELECT p.*, pc.slug AS cat_slug, pc.name AS cat_name, pc.icon AS cat_icon, pc.color AS cat_color
             FROM partners p
             LEFT JOIN partner_categories pc ON p.category_id = pc.id
             ORDER BY pc.sort_order ASC, p.sort_order ASC, p.name ASC"
        );

        // Group partners by category_id
        $grouped = [];
        foreach ($partners as $p) {
            $catId = $p['category_id'] ?? 0;
            $grouped[$catId][] = $p;
        }

        // Compute stats
        $totalPartners = count($partners);
        $totalCategories = count($categories);
        $activeCount = 0;
        $withLogo = 0;
        $withLink = 0;
        foreach ($partners as $p) {
            if ($p['is_active']) $activeCount++;
            if (!empty($p['logo_filename'])) $withLogo++;
            if (!empty($p['website'])) $withLink++;
        }

        $this->renderAdmin('templates/admin/partners/index.php', [
            'title'          => 'Partenaires',
            'categories'     => $categories,
            'grouped'        => $grouped,
            'totalPartners'  => $totalPartners,
            'totalCategories' => $totalCategories,
            'activeCount'    => $activeCount,
            'withLogo'       => $withLogo,
            'withLink'       => $withLink,
            'availableIcons' => self::ICONS,
            'availableColors' => self::COLORS,
        ]);
    }

    /**
     * Crée un nouveau partenaire
     */
    public function store(Request $request, array $params = []): void
    {
        $data = $request->all();

        if (empty($data['name'])) {
            set_flash('error', 'Le nom est obligatoire.');
            $this->redirect('/admin/partners');
            return;
        }

        $slug = slugify($data['name']);
        $existing = $this->db()->fetch("SELECT id FROM partners WHERE slug = ?", [$slug]);
        if ($existing) {
            $slug .= '-' . time();
        }

        // Handle logo upload
        $logoFilename = null;
        if (!empty($_FILES['logo_file']['tmp_name'])) {
            $logoFilename = $this->handleLogoUpload($_FILES['logo_file']);
        }

        // Next sort_order for this category
        $catId = !empty($data['category_id']) ? (int) $data['category_id'] : null;
        $maxOrder = $this->db()->fetch(
            "SELECT COALESCE(MAX(sort_order), 0) AS mx FROM partners WHERE category_id = ?",
            [$catId]
        );

        $this->db()->insert('partners', [
            'name'          => $data['name'],
            'slug'          => $slug,
            'description'   => $data['description'] ?? null,
            'website'       => !empty($data['website']) ? $data['website'] : null,
            'category_id'   => $catId,
            'logo_filename' => $logoFilename,
            'sort_order'    => (int) ($maxOrder['mx'] ?? 0) + 1,
            'is_active'     => ($data['is_active'] ?? '0') === '1' ? 1 : 0,
        ]);

        set_flash('success', 'Partenaire créé avec succès.');
        $this->redirect('/admin/partners');
    }

    /**
     * Met à jour un partenaire existant
     */
    public function update(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $partner = $this->db()->fetch("SELECT * FROM partners WHERE id = ?", [$id]);
        if (!$partner) {
            set_flash('error', 'Partenaire introuvable.');
            $this->redirect('/admin/partners');
            return;
        }

        $data = $request->all();

        if (empty($data['name'])) {
            set_flash('error', 'Le nom est obligatoire.');
            $this->redirect('/admin/partners');
            return;
        }

        $slug = slugify($data['name']);
        $existing = $this->db()->fetch("SELECT id FROM partners WHERE slug = ? AND id != ?", [$slug, $id]);
        if ($existing) {
            $slug .= '-' . time();
        }

        // Handle logo upload
        $logoFilename = $partner['logo_filename'];
        if (!empty($_FILES['logo_file']['tmp_name'])) {
            // Remove old logo
            if ($logoFilename) {
                $this->removeUpload($logoFilename);
            }
            $logoFilename = $this->handleLogoUpload($_FILES['logo_file']);
        }

        // Handle logo removal
        if (!empty($data['remove_logo']) && $data['remove_logo'] === '1') {
            if ($logoFilename) {
                $this->removeUpload($logoFilename);
            }
            $logoFilename = null;
        }

        $this->db()->update('partners', [
            'name'          => $data['name'],
            'slug'          => $slug,
            'description'   => $data['description'] ?? null,
            'website'       => !empty($data['website']) ? $data['website'] : null,
            'category_id'   => !empty($data['category_id']) ? (int) $data['category_id'] : null,
            'logo_filename' => $logoFilename,
            'is_active'     => ($data['is_active'] ?? '0') === '1' ? 1 : 0,
        ], 'id = ?', [$id]);

        set_flash('success', 'Partenaire mis à jour.');
        $this->redirect('/admin/partners');
    }

    /**
     * Supprime un partenaire
     */
    public function destroy(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $partner = $this->db()->fetch("SELECT logo_filename FROM partners WHERE id = ?", [$id]);

        if ($partner && $partner['logo_filename']) {
            $this->removeUpload($partner['logo_filename']);
        }

        $this->db()->delete('partners', 'id = ?', [$id]);
        set_flash('success', 'Partenaire supprimé.');
        $this->redirect('/admin/partners');
    }

    /**
     * Crée une nouvelle catégorie
     */
    public function storeCategory(Request $request, array $params = []): void
    {
        $data = $request->all();

        if (empty($data['name'])) {
            set_flash('error', 'Le nom de la catégorie est obligatoire.');
            $this->redirect('/admin/partners');
            return;
        }

        $slug = slugify($data['name']);
        $existing = $this->db()->fetch("SELECT id FROM partner_categories WHERE slug = ?", [$slug]);
        if ($existing) {
            $slug .= '-' . time();
        }

        $maxOrder = $this->db()->fetch(
            "SELECT COALESCE(MAX(sort_order), 0) AS mx FROM partner_categories"
        );

        $this->db()->insert('partner_categories', [
            'name'       => $data['name'],
            'slug'       => $slug,
            'icon'       => $data['icon'] ?? 'heart',
            'color'      => $data['color'] ?? '#3B82F6',
            'sort_order' => (int) ($data['sort_order'] ?? ((int) ($maxOrder['mx'] ?? 0) + 1)),
        ]);

        set_flash('success', 'Catégorie créée.');
        $this->redirect('/admin/partners');
    }

    /**
     * Met à jour une catégorie
     */
    public function updateCategory(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $data = $request->all();

        if (empty($data['name'])) {
            set_flash('error', 'Le nom de la catégorie est obligatoire.');
            $this->redirect('/admin/partners');
            return;
        }

        $slug = slugify($data['name']);
        $existing = $this->db()->fetch("SELECT id FROM partner_categories WHERE slug = ? AND id != ?", [$slug, $id]);
        if ($existing) {
            $slug .= '-' . time();
        }

        $this->db()->update('partner_categories', [
            'name'       => $data['name'],
            'slug'       => $slug,
            'icon'       => $data['icon'] ?? 'heart',
            'color'      => $data['color'] ?? '#3B82F6',
            'sort_order' => (int) ($data['sort_order'] ?? 0),
        ], 'id = ?', [$id]);

        set_flash('success', 'Catégorie mise à jour.');
        $this->redirect('/admin/partners');
    }

    /**
     * Supprime une catégorie (les partenaires perdent leur catégorie)
     */
    public function destroyCategory(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);

        // Detach partners from this category
        $this->db()->update('partners', ['category_id' => null], 'category_id = ?', [$id]);
        $this->db()->delete('partner_categories', 'id = ?', [$id]);

        set_flash('success', 'Catégorie supprimée.');
        $this->redirect('/admin/partners');
    }

    /**
     * Handle logo upload
     */
    private function handleLogoUpload(array $file): ?string
    {
        $allowed = ['image/png', 'image/jpeg', 'image/gif', 'image/svg+xml', 'image/webp'];
        if (!in_array($file['type'], $allowed, true)) {
            return null;
        }

        if ($file['size'] > 5 * 1024 * 1024) {
            return null;
        }

        $dir = $this->getUploadDir();
        $ext = pathinfo($file['name'], PATHINFO_EXTENSION);
        $filename = 'logo_' . uniqid() . '.' . strtolower($ext);

        if (move_uploaded_file($file['tmp_name'], $dir . $filename)) {
            return $filename;
        }

        return null;
    }

    private function getUploadDir(): string
    {
        $dir = dirname(__DIR__, 3) . '/public/uploads/partenaires/';
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
        return $dir;
    }

    private function removeUpload(string $filename): void
    {
        $path = dirname(__DIR__, 3) . '/public/uploads/partenaires/' . $filename;
        if (file_exists($path)) {
            unlink($path);
        }
    }
}
