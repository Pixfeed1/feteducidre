<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;

/**
 * Contrôleur CRUD pour la gestion des produits.
 * Gère la boutique : cidres, jus, coffrets, etc.
 */
class ProductAdminController extends Controller
{
    /**
     * Liste tous les produits
     */
    public function index(Request $request, array $params = []): void
    {
        $products = $this->db()->fetchAll(
            "SELECT * FROM products ORDER BY sort_order ASC, name ASC"
        );

        $this->renderAdmin('templates/admin/products/index.php', [
            'title'    => 'Produits',
            'products' => $products,
        ]);
    }

    /**
     * Affiche le formulaire de création d'un produit
     */
    public function create(Request $request, array $params = []): void
    {
        $this->renderAdmin('templates/admin/products/form.php', [
            'title'   => 'Nouveau produit',
            'product' => null,
        ]);
    }

    /**
     * Enregistre un nouveau produit
     */
    public function store(Request $request, array $params = []): void
    {
        $data = $request->all();

        if (empty($data['name']) || empty($data['price'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'Le nom et le prix sont obligatoires.');
            $this->redirect('/admin/products/create');
            return;
        }

        $slug = !empty($data['slug']) ? slugify($data['slug']) : slugify($data['name']);

        // Vérifier l'unicité du slug
        $existing = $this->db()->fetch("SELECT id FROM products WHERE slug = ?", [$slug]);
        if ($existing) {
            $slug .= '-' . time();
        }

        $this->db()->insert('products', [
            'name'               => $data['name'],
            'slug'               => $slug,
            'description'        => sanitize($data['description'] ?? ''),
            'short_description'  => $data['short_description'] ?? '',
            'price'              => (float) $data['price'],
            'sale_price'         => !empty($data['sale_price']) ? (float) $data['sale_price'] : null,
            'sku'                => $data['sku'] ?? null,
            'stock'              => (int) ($data['stock'] ?? 0),
            'weight'             => !empty($data['weight']) ? (float) $data['weight'] : null,
            'volume'             => $data['volume'] ?? null,
            'alcohol_percentage' => !empty($data['alcohol_percentage']) ? (float) $data['alcohol_percentage'] : null,
            'category'           => $data['category'] ?? null,
            'is_featured'        => isset($data['is_featured']) ? 1 : 0,
            'is_active'          => isset($data['is_active']) ? 1 : 0,
            'sort_order'         => (int) ($data['sort_order'] ?? 0),
        ]);

        set_flash('success', 'Produit créé avec succès.');
        $this->redirect('/admin/products');
    }

    /**
     * Affiche le formulaire de modification d'un produit
     */
    public function edit(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $product = $this->db()->fetch("SELECT * FROM products WHERE id = ?", [$id]);

        if (!$product) {
            set_flash('error', 'Produit introuvable.');
            $this->redirect('/admin/products');
            return;
        }

        $this->renderAdmin('templates/admin/products/form.php', [
            'title'   => 'Modifier : ' . $product['name'],
            'product' => $product,
        ]);
    }

    /**
     * Met à jour un produit existant
     */
    public function update(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $data = $request->all();

        if (empty($data['name']) || empty($data['price'])) {
            $_SESSION['_old_input'] = $data;
            set_flash('error', 'Le nom et le prix sont obligatoires.');
            $this->redirect('/admin/products/' . $id . '/edit');
            return;
        }

        $slug = !empty($data['slug']) ? slugify($data['slug']) : slugify($data['name']);

        $existing = $this->db()->fetch("SELECT id FROM products WHERE slug = ? AND id != ?", [$slug, $id]);
        if ($existing) {
            $slug .= '-' . time();
        }

        $this->db()->update('products', [
            'name'               => $data['name'],
            'slug'               => $slug,
            'description'        => sanitize($data['description'] ?? ''),
            'short_description'  => $data['short_description'] ?? '',
            'price'              => (float) $data['price'],
            'sale_price'         => !empty($data['sale_price']) ? (float) $data['sale_price'] : null,
            'sku'                => $data['sku'] ?? null,
            'stock'              => (int) ($data['stock'] ?? 0),
            'weight'             => !empty($data['weight']) ? (float) $data['weight'] : null,
            'volume'             => $data['volume'] ?? null,
            'alcohol_percentage' => !empty($data['alcohol_percentage']) ? (float) $data['alcohol_percentage'] : null,
            'category'           => $data['category'] ?? null,
            'is_featured'        => isset($data['is_featured']) ? 1 : 0,
            'is_active'          => isset($data['is_active']) ? 1 : 0,
            'sort_order'         => (int) ($data['sort_order'] ?? 0),
        ], 'id = ?', [$id]);

        set_flash('success', 'Produit mis à jour avec succès.');
        $this->redirect('/admin/products');
    }

    /**
     * Supprime un produit
     */
    public function destroy(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);
        $this->db()->delete('products', 'id = ?', [$id]);

        set_flash('success', 'Produit supprimé.');
        $this->redirect('/admin/products');
    }
}
