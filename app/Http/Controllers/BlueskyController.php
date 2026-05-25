<?php

namespace App\Http\Controllers;

use App\Models\Bluesky;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class BlueskyController extends Controller
{
    public function index(Request $request): Response
    {
        $filters = $request->only(['search', 'profession']);

        $jobs = Bluesky::query()
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('profession', 'ilike', "%{$search}%")
                        ->orWhere('facility', 'ilike', "%{$search}%")
                        ->orWhere('job_id', 'ilike', "%{$search}%");
                });
            })
          
            ->when($filters['profession'] ?? null, function ($query, $profession) {
                $query->where('profession', $profession);
            })
            ->orderBy('last_seen', 'desc')
            ->paginate(10)
            ->withQueryString();

        return Inertia::render('Bluesky/index', [
            'jobs' => $jobs,
            'filters' => $filters,
            'professions' => Bluesky::distinct()->pluck('profession'),
        ]);
    }
}
