<?php

declare(strict_types=1);

/**
 * Helpers texte — fonctions utilitaires pour le traitement de texte
 */

/**
 * Génère un slug propre à partir d'une chaîne
 */
function slugify(string $text): string
{
    // Translittération des caractères accentués
    $text = transliterator_transliterate('Any-Latin; Latin-ASCII; Lower()', $text);
    // Remplacer les caractères non-alphanumériques par des tirets
    $text = preg_replace('/[^a-z0-9]+/', '-', $text);
    // Supprimer les tirets en début/fin
    return trim($text, '-');
}

/**
 * Tronque un texte proprement (sur un mot entier)
 */
function truncate(string $text, int $length = 160, string $suffix = '…'): string
{
    $text = strip_tags($text);

    if (mb_strlen($text) <= $length) {
        return $text;
    }

    $truncated = mb_substr($text, 0, $length);
    $lastSpace = mb_strrpos($truncated, ' ');

    if ($lastSpace !== false) {
        $truncated = mb_substr($truncated, 0, $lastSpace);
    }

    return rtrim($truncated, '.,!?;: ') . $suffix;
}

/**
 * Nettoie le HTML en ne gardant que les balises autorisées
 */
function sanitize(string $html): string
{
    $allowed = '<p><br><strong><em><b><i><u><a><ul><ol><li><h2><h3><h4><h5><h6><blockquote><img><figure><figcaption><table><thead><tbody><tr><th><td>';
    return strip_tags($html, $allowed);
}

/**
 * Génère un extrait à partir d'un contenu HTML
 */
function excerpt(string $html, int $length = 160): string
{
    return truncate(strip_tags($html), $length);
}

/**
 * Formate une taille de fichier en unité lisible
 */
function format_file_size(int $bytes): string
{
    if ($bytes < 1024) {
        return $bytes . ' o';
    }
    if ($bytes < 1024 * 1024) {
        return round($bytes / 1024) . ' Ko';
    }
    return number_format($bytes / (1024 * 1024), 1, ',', '') . ' Mo';
}
