<?php

declare(strict_types=1);

namespace App\Services;

use App\Core\Config;

/**
 * Service SEO — génère les meta tags, Open Graph et JSON-LD.
 */
class SeoService
{
    /**
     * Génère les balises meta pour une page
     */
    public static function meta(array $seo): string
    {
        $html = '';

        // Title
        if (!empty($seo['title'])) {
            $html .= '<title>' . htmlspecialchars($seo['title']) . '</title>' . "\n";
        }

        // Description
        if (!empty($seo['description'])) {
            $html .= '<meta name="description" content="' . htmlspecialchars($seo['description']) . '">' . "\n";
        }

        // Canonical
        if (!empty($seo['canonical'])) {
            $html .= '<link rel="canonical" href="' . htmlspecialchars($seo['canonical']) . '">' . "\n";
        }

        // Robots
        if (!empty($seo['noindex'])) {
            $html .= '<meta name="robots" content="noindex, nofollow">' . "\n";
        }

        return $html;
    }

    /**
     * Génère les balises Open Graph
     */
    public static function openGraph(array $seo): string
    {
        $html = '<meta property="og:type" content="' . ($seo['og_type'] ?? 'website') . '">' . "\n";
        $html .= '<meta property="og:locale" content="fr_FR">' . "\n";
        $html .= '<meta property="og:site_name" content="Fête du Cidre">' . "\n";

        if (!empty($seo['title'])) {
            $html .= '<meta property="og:title" content="' . htmlspecialchars($seo['title']) . '">' . "\n";
        }
        if (!empty($seo['description'])) {
            $html .= '<meta property="og:description" content="' . htmlspecialchars($seo['description']) . '">' . "\n";
        }
        if (!empty($seo['canonical'])) {
            $html .= '<meta property="og:url" content="' . htmlspecialchars($seo['canonical']) . '">' . "\n";
        }
        if (!empty($seo['image'])) {
            $html .= '<meta property="og:image" content="' . htmlspecialchars($seo['image']) . '">' . "\n";
        }

        return $html;
    }

    /**
     * Génère le JSON-LD pour l'organisation
     */
    public static function jsonLdOrganization(): string
    {
        $data = [
            '@context'    => 'https://schema.org',
            '@type'       => 'Organization',
            'name'        => 'Association Fête du Cidre',
            'url'         => Config::baseUrl(),
            'description' => 'Association loi 1901 organisant la Fête du Cidre à L\'Hôtellerie de Flée (49500) depuis 1989.',
            'address'     => [
                '@type'           => 'PostalAddress',
                'addressLocality' => 'L\'Hôtellerie de Flée',
                'postalCode'      => '49500',
                'addressCountry'  => 'FR',
            ],
        ];

        return '<script type="application/ld+json">' . json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>';
    }

    /**
     * Génère le JSON-LD pour un événement
     */
    public static function jsonLdEvent(string $name, string $date, string $location): string
    {
        $data = [
            '@context'  => 'https://schema.org',
            '@type'     => 'Event',
            'name'      => $name,
            'startDate' => $date,
            'location'  => [
                '@type'   => 'Place',
                'name'    => $location,
                'address' => [
                    '@type'           => 'PostalAddress',
                    'addressLocality' => 'L\'Hôtellerie de Flée',
                    'postalCode'      => '49500',
                    'addressCountry'  => 'FR',
                ],
            ],
            'organizer' => [
                '@type' => 'Organization',
                'name'  => 'Association Fête du Cidre',
                'url'   => Config::baseUrl(),
            ],
        ];

        return '<script type="application/ld+json">' . json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>';
    }

    /**
     * Génère le JSON-LD pour un produit
     */
    public static function jsonLdProduct(array $product): string
    {
        $data = [
            '@context'    => 'https://schema.org',
            '@type'       => 'Product',
            'name'        => $product['name'],
            'description' => $product['description'] ?? '',
            'url'         => Config::baseUrl() . '/boutique/' . $product['slug'],
            'offers'      => [
                '@type'         => 'Offer',
                'price'         => number_format((float)$product['price'], 2, '.', ''),
                'priceCurrency' => 'EUR',
                'availability'  => ($product['stock'] ?? 0) > 0
                    ? 'https://schema.org/InStock'
                    : 'https://schema.org/OutOfStock',
            ],
        ];

        return '<script type="application/ld+json">' . json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>';
    }
}
