<?php

declare(strict_types=1);

namespace App\Controllers\Front;

use App\Core\Controller;
use App\Core\Config;
use App\Core\Request;
use App\Core\Response;
use App\Services\PaymentService;

/**
 * Contrôleur de la boutique en ligne.
 * Gère le catalogue produits, le panier et le processus de commande.
 */
class ShopController extends Controller
{
    /**
     * Liste tous les produits actifs, groupés par catégorie.
     */
    public function index(Request $request, array $params = []): void
    {
        $db = $this->db();

        $page = $db->fetch(
            "SELECT id, title, slug, content, meta_title, meta_description FROM pages WHERE slug = ? AND status = ?",
            ['boutique', 'published']
        );

        // Récupérer tous les produits actifs avec image
        $products = $db->fetchAll(
            "SELECT p.id, p.name, p.slug, p.short_description, p.price, p.sale_price,
                    p.volume, p.alcohol_percentage, p.category, p.is_featured,
                    m.filename, m.alt_text, m.width, m.height,
                    m.dominant_color, m.has_webp, m.has_avif, m.sizes
             FROM products p
             LEFT JOIN media m ON p.image_id = m.id
             WHERE p.is_active = 1
             ORDER BY p.sort_order ASC, p.name ASC"
        );

        // Construire les objets image et extraire les catégories
        $categories = [];
        foreach ($products as &$product) {
            $product['image'] = null;
            if ($product['filename']) {
                $product['image'] = [
                    'filename'       => $product['filename'],
                    'alt_text'       => $product['alt_text'],
                    'width'          => $product['width'],
                    'height'         => $product['height'],
                    'dominant_color' => $product['dominant_color'],
                    'has_webp'       => $product['has_webp'],
                    'has_avif'       => $product['has_avif'],
                    'sizes'          => $product['sizes'],
                ];
            }
            $cat = $product['category'] ?: 'autres';
            if (!in_array($cat, $categories, true)) {
                $categories[] = $cat;
            }
        }
        unset($product);

        // SEO
        $seo = [
            'title'       => 'Boutique — Fête du Cidre',
            'description' => 'Cidres, jus de pomme, pommeau… retrouvez les saveurs du terroir du Haut Anjou.',
            'canonical'   => Config::baseUrl() . '/boutique',
        ];

        $this->render('templates/front/shop/index.php', [
            'page'       => $page,
            'products'   => $products,
            'categories' => $categories,
            'seo'        => $seo,
        ]);
    }

    /**
     * Affiche un produit par son slug.
     */
    public function show(Request $request, array $params = []): void
    {
        $slug = $params['slug'] ?? '';
        $db = $this->db();

        $product = $db->fetch(
            "SELECT id, name, slug, description, short_description, price, sale_price,
                    volume, alcohol_percentage, category, image_id, gallery,
                    meta_title, meta_description, stock
             FROM products WHERE slug = ? AND is_active = 1",
            [$slug]
        );

        if (!$product) {
            Response::notFound();
            return;
        }

        // Récupérer l'image principale si définie
        $image = null;
        if ($product['image_id']) {
            $image = $db->fetch(
                "SELECT id, filename, alt_text, width, height, dominant_color, has_webp, has_avif, sizes
                 FROM media WHERE id = ?",
                [(int) $product['image_id']]
            );
        }

        // Produits similaires (même catégorie, max 3)
        $related = [];
        if ($product['category']) {
            $related = $db->fetchAll(
                "SELECT p.id, p.name, p.slug, p.price, p.sale_price, p.category,
                        m.filename, m.alt_text
                 FROM products p
                 LEFT JOIN media m ON p.image_id = m.id
                 WHERE p.is_active = 1 AND p.category = ? AND p.id != ?
                 ORDER BY p.sort_order ASC
                 LIMIT 3",
                [$product['category'], (int) $product['id']]
            );
        }

        // SEO
        $seo = [
            'title'       => $product['meta_title'] ?: $product['name'] . ' — Boutique Fête du Cidre',
            'description' => $product['meta_description'] ?: excerpt($product['description'] ?? '', 160),
            'canonical'   => Config::baseUrl() . '/boutique/' . $product['slug'],
        ];

        $this->render('templates/front/shop/product.php', [
            'product' => $product,
            'image'   => $image,
            'related' => $related,
            'seo'     => $seo,
        ]);
    }

    /**
     * Affiche le panier depuis la session.
     */
    public function cart(Request $request, array $params = []): void
    {
        $db = $this->db();
        $cart = $_SESSION['cart'] ?? [];
        $items = [];
        $subtotal = 0.0;

        // Enrichir chaque article du panier avec les données produit actuelles
        foreach ($cart as $productId => $cartItem) {
            $product = $db->fetch(
                "SELECT id, name, slug, price, sale_price, volume, image_id, stock
                 FROM products WHERE id = ? AND is_active = 1",
                [(int) $productId]
            );

            if ($product) {
                $unitPrice = $product['sale_price'] ?: $product['price'];
                $quantity = (int) $cartItem['quantity'];
                $lineTotal = (float) $unitPrice * $quantity;
                $subtotal += $lineTotal;

                $items[] = [
                    'product'    => $product,
                    'quantity'   => $quantity,
                    'unit_price' => (float) $unitPrice,
                    'total'      => $lineTotal,
                ];
            }
        }

        // Récupérer les frais de livraison depuis les paramètres
        $shippingSetting = $db->fetch(
            "SELECT value FROM settings WHERE `group` = ? AND `key` = ?",
            ['shop', 'shipping_cost']
        );
        $shipping = (float) ($shippingSetting['value'] ?? 5.00);

        // Total
        $total = $subtotal + ($subtotal > 0 ? $shipping : 0.0);

        // SEO
        $seo = [
            'title'       => 'Panier — Fête du Cidre',
            'description' => 'Votre panier d\'achat.',
            'canonical'   => Config::baseUrl() . '/panier',
        ];

        $this->render('templates/front/shop/cart.php', [
            'items'    => $items,
            'subtotal' => $subtotal,
            'shipping' => $shipping,
            'total'    => $total,
            'seo'      => $seo,
        ]);
    }

    /**
     * Ajoute un produit au panier (POST).
     */
    public function addToCart(Request $request, array $params = []): void
    {
        if (!$this->validateCsrf($request, '/boutique')) {
            return;
        }

        $productId = (int) $request->post('product_id', '0');
        $quantity = max(1, (int) $request->post('quantity', '1'));

        // Vérifier que le produit existe et est actif
        $db = $this->db();
        $product = $db->fetch(
            "SELECT id, name, stock FROM products WHERE id = ? AND is_active = 1",
            [$productId]
        );

        if (!$product) {
            set_flash('error', 'Ce produit n\'existe pas ou n\'est plus disponible.');
            Response::redirect('/boutique');
            return;
        }

        // Vérifier le stock
        $currentQty = (int) ($_SESSION['cart'][$productId]['quantity'] ?? 0);
        if ($product['stock'] > 0 && ($currentQty + $quantity) > $product['stock']) {
            set_flash('warning', 'Stock insuffisant pour ce produit.');
            Response::redirect('/panier');
            return;
        }

        // Ajouter ou mettre à jour le panier
        if (!isset($_SESSION['cart'])) {
            $_SESSION['cart'] = [];
        }

        if (isset($_SESSION['cart'][$productId])) {
            $_SESSION['cart'][$productId]['quantity'] += $quantity;
        } else {
            $_SESSION['cart'][$productId] = [
                'product_id' => $productId,
                'quantity'   => $quantity,
            ];
        }

        set_flash('success', e($product['name']) . ' a été ajouté au panier.');
        Response::redirect('/panier');
    }

    /**
     * Met à jour la quantité d'un article du panier (POST).
     */
    public function updateCart(Request $request, array $params = []): void
    {
        if (!$this->validateCsrf($request, '/panier')) {
            return;
        }

        $productId = (int) $request->post('product_id', '0');
        $quantity = (int) $request->post('quantity', '1');

        if ($quantity <= 0) {
            unset($_SESSION['cart'][$productId]);
        } elseif (isset($_SESSION['cart'][$productId])) {
            $_SESSION['cart'][$productId]['quantity'] = $quantity;
        }

        set_flash('success', 'Le panier a été mis à jour.');
        Response::redirect('/panier');
    }

    /**
     * Supprime un article du panier (POST).
     */
    public function removeFromCart(Request $request, array $params = []): void
    {
        if (!$this->validateCsrf($request, '/panier')) {
            return;
        }

        $productId = (int) $request->post('product_id', '0');
        unset($_SESSION['cart'][$productId]);

        set_flash('success', 'L\'article a été retiré du panier.');
        Response::redirect('/panier');
    }

    /**
     * Affiche le formulaire de commande.
     */
    public function checkout(Request $request, array $params = []): void
    {
        // Vérifier que le panier n'est pas vide
        if (empty($_SESSION['cart'])) {
            set_flash('warning', 'Votre panier est vide.');
            Response::redirect('/boutique');
            return;
        }

        $db = $this->db();
        $cart = $_SESSION['cart'];
        $items = [];
        $subtotal = 0.0;

        foreach ($cart as $productId => $cartItem) {
            $product = $db->fetch(
                "SELECT id, name, slug, price, sale_price, volume, category
                 FROM products WHERE id = ? AND is_active = 1",
                [(int) $productId]
            );

            if ($product) {
                $unitPrice = $product['sale_price'] ?: $product['price'];
                $quantity = (int) $cartItem['quantity'];
                $lineTotal = (float) $unitPrice * $quantity;
                $subtotal += $lineTotal;

                $items[] = [
                    'product'    => $product,
                    'quantity'   => $quantity,
                    'unit_price' => (float) $unitPrice,
                    'total'      => $lineTotal,
                ];
            }
        }

        // Frais de livraison
        $shippingSetting = $db->fetch(
            "SELECT value FROM settings WHERE `group` = ? AND `key` = ?",
            ['shop', 'shipping_cost']
        );
        $shipping = (float) ($shippingSetting['value'] ?? 5.00);
        $total = $subtotal + $shipping;

        // SEO
        $seo = [
            'title'       => 'Commande — Fête du Cidre',
            'description' => 'Finalisez votre commande.',
            'canonical'   => Config::baseUrl() . '/commande',
        ];

        $this->render('templates/front/shop/checkout.php', [
            'items'    => $items,
            'subtotal' => $subtotal,
            'shipping' => $shipping,
            'total'    => $total,
            'seo'      => $seo,
        ]);
    }

    /**
     * Traite la soumission du formulaire de commande (POST).
     */
    public function processCheckout(Request $request, array $params = []): void
    {
        if (!$this->validateCsrf($request, '/commande')) {
            return;
        }

        // Vérifier que le panier n'est pas vide
        if (empty($_SESSION['cart'])) {
            set_flash('warning', 'Votre panier est vide.');
            Response::redirect('/boutique');
            return;
        }

        // Récupérer et valider les données du formulaire
        $firstName   = $request->post('first_name', '');
        $lastName    = $request->post('last_name', '');
        $email       = $request->post('email', '');
        $phone       = $request->post('phone', '');
        $address     = $request->post('address', '');
        $city        = $request->post('city', '');
        $postalCode  = $request->post('postal_code', '');
        $notes       = $request->post('notes', '');

        $errors = [];
        if (empty($firstName)) {
            $errors[] = 'Le prénom est requis.';
        }
        if (empty($lastName)) {
            $errors[] = 'Le nom est requis.';
        }
        if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $errors[] = 'Une adresse email valide est requise.';
        }
        if (empty($address)) {
            $errors[] = 'L\'adresse est requise.';
        }
        if (empty($city)) {
            $errors[] = 'La ville est requise.';
        }
        if (empty($postalCode)) {
            $errors[] = 'Le code postal est requis.';
        }

        if (!empty($errors)) {
            $_SESSION['_old_input'] = $request->all();
            set_flash('error', implode(' ', $errors));
            Response::redirect('/commande');
            return;
        }

        $db = $this->db();

        // Calculer les totaux
        $cart = $_SESSION['cart'];
        $subtotal = 0.0;
        $orderItems = [];

        foreach ($cart as $productId => $cartItem) {
            $product = $db->fetch(
                "SELECT id, name, sku, price, sale_price, stock
                 FROM products WHERE id = ? AND is_active = 1",
                [(int) $productId]
            );

            if (!$product) {
                continue;
            }

            $unitPrice = $product['sale_price'] ?: $product['price'];
            $quantity = (int) $cartItem['quantity'];
            $lineTotal = (float) $unitPrice * $quantity;
            $subtotal += $lineTotal;

            $orderItems[] = [
                'product_id'   => (int) $product['id'],
                'product_name' => $product['name'],
                'product_sku'  => $product['sku'],
                'quantity'     => $quantity,
                'unit_price'   => (float) $unitPrice,
                'total_price'  => $lineTotal,
            ];
        }

        if (empty($orderItems)) {
            set_flash('error', 'Aucun produit valide dans le panier.');
            Response::redirect('/boutique');
            return;
        }

        // Frais de livraison
        $shippingSetting = $db->fetch(
            "SELECT value FROM settings WHERE `group` = ? AND `key` = ?",
            ['shop', 'shipping_cost']
        );
        $shipping = (float) ($shippingSetting['value'] ?? 5.00);
        $total = $subtotal + $shipping;

        // Générer la référence unique
        $reference = 'CMD-' . strtoupper(date('Ymd')) . '-' . strtoupper(bin2hex(random_bytes(4)));

        // Créer la commande en transaction
        $db->beginTransaction();
        try {
            $orderId = $db->insert('orders', [
                'reference'            => $reference,
                'status'               => 'pending',
                'customer_email'       => $email,
                'customer_first_name'  => $firstName,
                'customer_last_name'   => $lastName,
                'customer_phone'       => $phone,
                'shipping_address'     => $address,
                'shipping_city'        => $city,
                'shipping_postal_code' => $postalCode,
                'billing_address'      => $address,
                'billing_city'         => $city,
                'billing_postal_code'  => $postalCode,
                'subtotal'             => $subtotal,
                'shipping_cost'        => $shipping,
                'total'                => $total,
                'notes'                => $notes,
            ]);

            // Insérer les lignes de commande
            foreach ($orderItems as $item) {
                $db->insert('order_items', [
                    'order_id'     => $orderId,
                    'product_id'   => $item['product_id'],
                    'product_name' => $item['product_name'],
                    'product_sku'  => $item['product_sku'],
                    'quantity'     => $item['quantity'],
                    'unit_price'   => $item['unit_price'],
                    'total_price'  => $item['total_price'],
                ]);
            }

            $db->commit();
        } catch (\Exception $e) {
            $db->rollBack();
            set_flash('error', 'Une erreur est survenue lors de la création de la commande. Veuillez réessayer.');
            Response::redirect('/commande');
            return;
        }

        // Vider le panier
        unset($_SESSION['cart']);
        unset($_SESSION['_old_input']);

        // Récupérer le mode de paiement choisi
        $paymentMethod = $request->post('payment_method', 'card');

        // Paiement par carte via Stripe Checkout
        if ($paymentMethod === 'card' && PaymentService::isStripeConfigured()) {
            try {
                $orderData = [
                    'id'             => $orderId,
                    'reference'      => $reference,
                    'customer_email' => $email,
                ];
                $checkoutUrl = PaymentService::createCheckoutSession($orderData, $orderItems, $shipping);
                Response::redirect($checkoutUrl);
                return;
            } catch (\Exception $e) {
                // Si Stripe échoue, on tombe sur la confirmation classique
                set_flash('warning', 'Le paiement en ligne n\'a pas pu être initialisé. Vous pouvez régler par virement.');
            }
        }

        // Paiement par virement ou fallback : marquer comme virement
        $db->update(
            'orders',
            ['payment_method' => $paymentMethod === 'transfer' ? 'transfer' : 'pending'],
            'id = ?',
            [$orderId]
        );

        set_flash('success', 'Votre commande a bien été enregistrée !');
        Response::redirect('/commande/confirmation/' . $reference);
    }

    /**
     * Affiche la confirmation de commande.
     */
    public function confirmation(Request $request, array $params = []): void
    {
        $reference = $params['reference'] ?? '';
        $db = $this->db();

        $order = $db->fetch(
            "SELECT id, reference, status, customer_first_name, customer_last_name,
                    customer_email, customer_phone, shipping_address, shipping_city,
                    shipping_postal_code, subtotal, shipping_cost, total, created_at
             FROM orders WHERE reference = ?",
            [$reference]
        );

        if (!$order) {
            Response::notFound();
            return;
        }

        // Récupérer les lignes de commande
        $orderItems = $db->fetchAll(
            "SELECT product_name, quantity, unit_price, total_price
             FROM order_items WHERE order_id = ? ORDER BY id ASC",
            [(int) $order['id']]
        );

        // SEO
        $seo = [
            'title'       => 'Confirmation de commande — Fête du Cidre',
            'description' => 'Votre commande a bien été enregistrée.',
            'canonical'   => Config::baseUrl() . '/commande/confirmation/' . $reference,
        ];

        $this->render('templates/front/shop/confirmation.php', [
            'order'      => $order,
            'orderItems' => $orderItems,
            'seo'        => $seo,
        ]);
    }
}
