<?php

declare(strict_types=1);

/**
 * Helpers HTML — fonctions utilitaires pour les templates
 */

/**
 * Génère l'URL versionnée d'un asset (CSS/JS)
 */
function asset(string $path): string
{
    $basePath = dirname(__DIR__, 2) . '/public';
    $filePath = $basePath . '/' . ltrim($path, '/');

    // En prod, utiliser le manifest pour le versioning
    static $manifest = null;
    $manifestFile = $basePath . '/assets/manifest.json';

    if ($manifest === null && file_exists($manifestFile)) {
        $manifest = json_decode(file_get_contents($manifestFile), true) ?: [];
    }

    if ($manifest && isset($manifest[$path])) {
        return '/' . $manifest[$path];
    }

    // Fallback : ajouter le timestamp du fichier comme query string
    $version = file_exists($filePath) ? filemtime($filePath) : time();
    return '/' . ltrim($path, '/') . '?v=' . $version;
}

/**
 * Génère un élément <picture> complet avec WebP/AVIF et responsive
 *
 * @param array $image Données média depuis la DB
 * @param string $alt Texte alternatif
 * @param string $class Classes CSS
 * @param bool $aboveFold Si true : loading=eager + fetchpriority=high
 * @param string|null $sizes Attribut sizes pour responsive
 */
function img(array $image, string $alt = '', string $class = '', bool $aboveFold = false, ?string $sizes = null): string
{
    if (empty($image) || empty($image['filename'])) {
        return '';
    }

    $uploadPath = '/storage/uploads';

    $filename = $image['filename'];
    $nameWithoutExt = pathinfo($filename, PATHINFO_FILENAME);
    $width = $image['width'] ?? '';
    $height = $image['height'] ?? '';
    $dominantColor = $image['dominant_color'] ?? '#FAF5EC';
    $altText = e($alt ?: ($image['alt_text'] ?? ''));

    $loading = $aboveFold ? 'eager' : 'lazy';
    $fetchPriority = $aboveFold ? ' fetchpriority="high"' : '';
    $classAttr = $class ? ' class="' . e($class) . '"' : '';
    $sizesAttr = $sizes ? ' sizes="' . e($sizes) . '"' : '';

    // Style placeholder avec couleur dominante
    $style = "background-color:{$dominantColor};aspect-ratio:{$width}/{$height}";

    $html = '<picture>';

    // Source AVIF si disponible
    if (!empty($image['has_avif'])) {
        $srcsetParts = [];
        $imageSizes = !empty($image['sizes']) ? json_decode($image['sizes'], true) : [];
        if (is_array($imageSizes)) {
            foreach ($imageSizes as $size) {
                $srcsetParts[] = "{$uploadPath}/large/{$nameWithoutExt}-{$size}.avif {$size}w";
            }
        }
        $srcsetParts[] = "{$uploadPath}/large/{$nameWithoutExt}.avif";
        $html .= '<source type="image/avif" srcset="' . implode(', ', $srcsetParts) . '"' . $sizesAttr . '>';
    }

    // Source WebP si disponible
    if (!empty($image['has_webp'])) {
        $srcsetParts = [];
        $imageSizes = !empty($image['sizes']) ? json_decode($image['sizes'], true) : [];
        if (is_array($imageSizes)) {
            foreach ($imageSizes as $size) {
                $srcsetParts[] = "{$uploadPath}/large/{$nameWithoutExt}-{$size}.webp {$size}w";
            }
        }
        $srcsetParts[] = "{$uploadPath}/large/{$nameWithoutExt}.webp";
        $html .= '<source type="image/webp" srcset="' . implode(', ', $srcsetParts) . '"' . $sizesAttr . '>';
    }

    // Image fallback JPG
    $src = "{$uploadPath}/large/{$filename}";
    $html .= '<img src="' . $src . '"';
    $html .= ' alt="' . $altText . '"';
    $html .= $classAttr;
    $html .= ' loading="' . $loading . '"';
    $html .= $fetchPriority;
    if ($width) $html .= ' width="' . (int)$width . '"';
    if ($height) $html .= ' height="' . (int)$height . '"';
    $html .= ' style="' . $style . '"';
    $html .= ' decoding="async">';

    $html .= '</picture>';

    return $html;
}

/**
 * Échappe le HTML (shortcut pour htmlspecialchars)
 */
function e(?string $str): string
{
    return htmlspecialchars($str ?? '', ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/**
 * Retourne 'active' si la route courante correspond au chemin
 */
function active(string $path): string
{
    $current = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
    $current = rtrim($current, '/') ?: '/';
    $path = rtrim($path, '/') ?: '/';

    return $current === $path ? 'active' : '';
}

/**
 * Génère un champ hidden CSRF
 */
function csrf_field(): string
{
    $token = $_SESSION['csrf_token'] ?? '';
    if (empty($token)) {
        $token = bin2hex(random_bytes(32));
        $_SESSION['csrf_token'] = $token;
    }
    return '<input type="hidden" name="_csrf_token" value="' . e($token) . '">';
}

/**
 * Retourne la valeur précédente d'un champ de formulaire (après erreur de validation)
 */
function old(string $key, string $default = ''): string
{
    return e($_SESSION['_old_input'][$key] ?? $default);
}

/**
 * Génère l'URL d'une page à partir de son slug
 */
function page_url(string $slug): string
{
    if ($slug === 'accueil') {
        return '/';
    }
    return '/' . $slug;
}

/**
 * Affiche un message flash
 */
function flash(string $type = 'success'): string
{
    if (empty($_SESSION['flash'][$type])) {
        return '';
    }

    $message = e($_SESSION['flash'][$type]);
    unset($_SESSION['flash'][$type]);

    $iconMap = [
        'success' => 'check-circle',
        'error'   => 'alert-circle',
        'warning' => 'alert-triangle',
        'info'    => 'info',
    ];
    $icon = $iconMap[$type] ?? 'info';

    return '<div class="flash flash-' . $type . '">'
         . icon($icon, 20) . ' '
         . '<span>' . $message . '</span>'
         . '</div>';
}

/**
 * Définit un message flash
 */
function set_flash(string $type, string $message): void
{
    $_SESSION['flash'][$type] = $message;
}
