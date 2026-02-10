<?php

declare(strict_types=1);

namespace App\Services;

use App\Core\Config;
use App\Core\Database;

/**
 * Service de paiement — intégration Stripe Checkout.
 * Gère la création de sessions Stripe et la mise à jour des commandes via webhook.
 */
class PaymentService
{
    /**
     * Vérifie si Stripe est configuré.
     */
    public static function isStripeConfigured(): bool
    {
        $secret = Config::get('STRIPE_SECRET_KEY', '');
        $public = Config::get('STRIPE_PUBLIC_KEY', '');
        return !empty($secret) && !empty($public);
    }

    /**
     * Crée une session Stripe Checkout et retourne l'URL de redirection.
     *
     * @param array $order    Données de la commande (reference, total, id, etc.)
     * @param array $items    Lignes de commande (product_name, quantity, unit_price)
     * @param float $shipping Frais de livraison
     * @return string URL de la session Stripe Checkout
     */
    public static function createCheckoutSession(array $order, array $items, float $shipping): string
    {
        $secretKey = Config::get('STRIPE_SECRET_KEY', '');
        if (empty($secretKey)) {
            throw new \RuntimeException('Clé Stripe non configurée.');
        }

        \Stripe\Stripe::setApiKey($secretKey);

        // Construire les line_items pour Stripe
        $lineItems = [];
        foreach ($items as $item) {
            $lineItems[] = [
                'price_data' => [
                    'currency'     => 'eur',
                    'unit_amount'  => (int) round($item['unit_price'] * 100), // en centimes
                    'product_data' => [
                        'name' => $item['product_name'],
                    ],
                ],
                'quantity' => $item['quantity'],
            ];
        }

        // Ajouter les frais de livraison comme ligne
        if ($shipping > 0) {
            $lineItems[] = [
                'price_data' => [
                    'currency'     => 'eur',
                    'unit_amount'  => (int) round($shipping * 100),
                    'product_data' => [
                        'name' => 'Frais de livraison',
                    ],
                ],
                'quantity' => 1,
            ];
        }

        // Déterminer les URLs de callback
        $baseUrl = Config::get('APP_URL', '');
        $successUrl = $baseUrl . '/commande/confirmation/' . $order['reference'] . '?payment=success';
        $cancelUrl  = $baseUrl . '/commande/confirmation/' . $order['reference'] . '?payment=cancelled';

        $session = \Stripe\Checkout\Session::create([
            'payment_method_types' => ['card'],
            'line_items'           => $lineItems,
            'mode'                 => 'payment',
            'success_url'          => $successUrl,
            'cancel_url'           => $cancelUrl,
            'client_reference_id'  => $order['reference'],
            'customer_email'       => $order['customer_email'],
            'metadata'             => [
                'order_id'    => (string) $order['id'],
                'reference'   => $order['reference'],
            ],
        ]);

        // Stocker le Stripe Session ID dans la commande
        Database::getInstance()->update(
            'orders',
            ['payment_id' => $session->id],
            'id = ?',
            [(int) $order['id']]
        );

        return $session->url;
    }

    /**
     * Traite un événement webhook Stripe.
     *
     * @param string $payload   Corps brut de la requête
     * @param string $signature Header Stripe-Signature
     * @return bool True si le paiement a été confirmé
     */
    public static function handleWebhook(string $payload, string $signature): bool
    {
        $webhookSecret = Config::get('STRIPE_WEBHOOK_SECRET', '');
        if (empty($webhookSecret)) {
            throw new \RuntimeException('STRIPE_WEBHOOK_SECRET non configuré.');
        }

        \Stripe\Stripe::setApiKey(Config::get('STRIPE_SECRET_KEY', ''));

        $event = \Stripe\Webhook::constructEvent($payload, $signature, $webhookSecret);

        if ($event->type === 'checkout.session.completed') {
            $session = $event->data->object;
            $reference = $session->client_reference_id ?? ($session->metadata->reference ?? '');

            if (!empty($reference) && $session->payment_status === 'paid') {
                $db = Database::getInstance();
                $order = $db->fetch(
                    "SELECT id, status FROM orders WHERE reference = ?",
                    [$reference]
                );

                if ($order && $order['status'] === 'pending') {
                    $db->update(
                        'orders',
                        [
                            'status'         => 'paid',
                            'payment_method' => 'card',
                            'payment_id'     => $session->payment_intent ?? $session->id,
                        ],
                        'id = ?',
                        [(int) $order['id']]
                    );
                    return true;
                }
            }
        }

        return false;
    }
}
