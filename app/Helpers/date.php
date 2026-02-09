<?php

declare(strict_types=1);

/**
 * Helpers date — fonctions utilitaires pour les dates en français
 */

/**
 * Formate une date en français (ex: "14 juin 2025")
 */
function date_fr(?string $date, string $format = 'long'): string
{
    if (empty($date)) {
        return '';
    }

    $timestamp = strtotime($date);
    if ($timestamp === false) {
        return $date;
    }

    $months = [
        1 => 'janvier', 2 => 'février', 3 => 'mars', 4 => 'avril',
        5 => 'mai', 6 => 'juin', 7 => 'juillet', 8 => 'août',
        9 => 'septembre', 10 => 'octobre', 11 => 'novembre', 12 => 'décembre',
    ];

    $day = (int) date('j', $timestamp);
    $month = (int) date('n', $timestamp);
    $year = date('Y', $timestamp);

    return match ($format) {
        'short'    => $day . ' ' . mb_substr($months[$month], 0, 3) . '. ' . $year,
        'day'      => $day . ' ' . $months[$month],
        'month'    => $months[$month] . ' ' . $year,
        'datetime' => $day . ' ' . $months[$month] . ' ' . $year . ' à ' . date('H\hi', $timestamp),
        default    => $day . ' ' . $months[$month] . ' ' . $year,
    };
}

/**
 * Retourne le temps écoulé en français (ex: "Il y a 3 jours")
 */
function time_ago(string $date): string
{
    $timestamp = strtotime($date);
    if ($timestamp === false) {
        return $date;
    }

    $diff = time() - $timestamp;

    if ($diff < 0) {
        return 'dans le futur';
    }

    return match (true) {
        $diff < 60         => 'À l\'instant',
        $diff < 3600       => 'Il y a ' . floor($diff / 60) . ' min',
        $diff < 86400      => 'Il y a ' . floor($diff / 3600) . ' h',
        $diff < 172800     => 'Hier',
        $diff < 604800     => 'Il y a ' . floor($diff / 86400) . ' jours',
        $diff < 2592000    => 'Il y a ' . floor($diff / 604800) . ' semaines',
        $diff < 31536000   => 'Il y a ' . floor($diff / 2592000) . ' mois',
        default            => 'Il y a ' . floor($diff / 31536000) . ' ans',
    };
}

/**
 * Formate une durée en secondes (ex: "1h 23min 45s")
 */
function format_duration(int $seconds): string
{
    $hours = floor($seconds / 3600);
    $minutes = floor(($seconds % 3600) / 60);
    $secs = $seconds % 60;

    if ($hours > 0) {
        return sprintf('%dh %02dmin %02ds', $hours, $minutes, $secs);
    }
    if ($minutes > 0) {
        return sprintf('%dmin %02ds', $minutes, $secs);
    }
    return sprintf('%ds', $secs);
}
