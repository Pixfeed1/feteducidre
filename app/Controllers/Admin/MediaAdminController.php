<?php

declare(strict_types=1);

namespace App\Controllers\Admin;

use App\Core\Controller;
use App\Core\Request;
use App\Services\ImageService;

/**
 * Contrôleur pour la gestion des médias (upload AJAX).
 * Fournit des endpoints JSON pour l'upload et la suppression de fichiers.
 */
class MediaAdminController extends Controller
{
    /**
     * Upload d'un fichier via AJAX
     * Retourne une réponse JSON avec les informations du média créé.
     */
    public function upload(Request $request, array $params = []): void
    {
        $file = $request->file('file');

        if (!$file || $file['error'] !== UPLOAD_ERR_OK) {
            $this->json(['error' => 'Aucun fichier reçu ou erreur lors de l\'upload.'], 400);
            return;
        }

        try {
            $imageService = new ImageService();
            $result = $imageService->process($file);

            $this->json([
                'success'  => true,
                'media_id' => $result['id'],
                'filename' => $result['metadata']['filename'],
                'url'      => '/storage/uploads/large/' . $result['metadata']['filename'],
                'width'    => $result['metadata']['width'],
                'height'   => $result['metadata']['height'],
            ]);
        } catch (\Throwable $e) {
            $this->json([
                'error' => 'Erreur lors du traitement : ' . $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Supprime un média
     * Retourne une réponse JSON confirmant la suppression.
     */
    public function delete(Request $request, array $params = []): void
    {
        $id = (int) ($params['id'] ?? 0);

        if ($id <= 0) {
            $this->json(['error' => 'Identifiant invalide.'], 400);
            return;
        }

        try {
            $imageService = new ImageService();
            $deleted = $imageService->delete($id);

            if ($deleted) {
                $this->json(['success' => true, 'message' => 'Média supprimé.']);
            } else {
                $this->json(['error' => 'Média introuvable.'], 404);
            }
        } catch (\Throwable $e) {
            $this->json([
                'error' => 'Erreur lors de la suppression : ' . $e->getMessage(),
            ], 500);
        }
    }
}
