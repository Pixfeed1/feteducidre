<?php

declare(strict_types=1);

namespace App\Core;

/**
 * Gestionnaire des couleurs dynamiques de la charte graphique.
 * Les couleurs sont stockées en DB (table settings, group 'colors') avec fallback sur les défauts.
 */
class Theme
{
    /** Couleurs par défaut de la charte graphique */
    private const DEFAULT_COLORS = [
        'vert-profond'  => '#2C4A2E',
        'vert-mousse'   => '#4A6B3E',
        'vert-clair'    => '#7A9E6B',
        'orange-cidre'  => '#D4833B',
        'orange-doux'   => '#E8A95B',
        'creme'         => '#FAF5EC',
        'creme-fonce'   => '#F0E8D8',
        'brun'          => '#5C3D2E',
        'texte'         => '#2A2318',
        'blanc'         => '#FFFDF8',
    ];

    private static ?array $cachedColors = null;

    /**
     * Récupère les couleurs (DB + fallback défaut)
     */
    public static function getColors(): array
    {
        if (self::$cachedColors !== null) {
            return self::$cachedColors;
        }

        $colors = self::DEFAULT_COLORS;

        try {
            $db = Database::getInstance();
            $rows = $db->fetchAll(
                "SELECT `key`, value FROM settings WHERE `group` = ? AND type = ?",
                ['colors', 'color']
            );

            foreach ($rows as $row) {
                if (isset($colors[$row['key']]) && preg_match('/^#[0-9a-fA-F]{6}$/', $row['value'])) {
                    $colors[$row['key']] = $row['value'];
                }
            }
        } catch (\Exception) {
            // Fallback silencieux sur les couleurs par défaut
        }

        self::$cachedColors = $colors;
        return $colors;
    }

    /**
     * Génère le bloc CSS :root avec les variables de couleurs
     */
    public static function cssVariables(): string
    {
        $colors = self::getColors();
        $css = ':root{';

        foreach ($colors as $name => $hex) {
            $css .= "--{$name}:{$hex};";
        }

        $css .= '}';
        return $css;
    }

    /**
     * Sauvegarde une couleur en DB (UPSERT)
     */
    public static function saveColor(string $name, string $hex): bool
    {
        if (!preg_match('/^#[0-9a-fA-F]{6}$/', $hex)) {
            return false;
        }

        if (!isset(self::DEFAULT_COLORS[$name])) {
            return false;
        }

        $db = Database::getInstance();

        // UPSERT via INSERT ... ON DUPLICATE KEY UPDATE
        $db->query(
            "INSERT INTO settings (`group`, `key`, value, type, label)
             VALUES (?, ?, ?, 'color', ?)
             ON DUPLICATE KEY UPDATE value = VALUES(value), updated_at = NOW()",
            ['colors', $name, $hex, ucfirst(str_replace('-', ' ', $name))]
        );

        // Invalider le cache
        self::$cachedColors = null;

        return true;
    }

    /**
     * Réinitialise toutes les couleurs aux défauts
     */
    public static function resetColors(): void
    {
        $db = Database::getInstance();
        $db->query("DELETE FROM settings WHERE `group` = ?", ['colors']);

        // Réinsérer les défauts
        foreach (self::DEFAULT_COLORS as $name => $hex) {
            $db->insert('settings', [
                'group' => 'colors',
                'key'   => $name,
                'value' => $hex,
                'type'  => 'color',
                'label' => ucfirst(str_replace('-', ' ', $name)),
            ]);
        }

        self::$cachedColors = null;
    }

    /**
     * Retourne les couleurs par défaut
     */
    public static function getDefaultColors(): array
    {
        return self::DEFAULT_COLORS;
    }
}
