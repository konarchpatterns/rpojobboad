<?php

namespace App\Http\Controllers;

use App\Models\Laboredge;
use App\Models\VmsCandidate;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class LaboredgeController extends Controller
{
    public function index(Request $request): Response
    {
        $filters = $request->only(['search', 'status', 'profession']);

        $jobs = Laboredge::query()
            ->with('details')
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('profession', 'ilike', "%{$search}%")
                        ->orWhere('facility', 'ilike', "%{$search}%")
                        ->orWhere('job_id', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['status'] ?? null, function ($query, $status) {
                $query->where('status', $status);
            })
            ->when($filters['profession'] ?? null, function ($query, $profession) {
                $query->where('profession', $profession);
            })
            ->orderBy('last_seen', 'desc')
            ->paginate(10)
            ->withQueryString();

        return Inertia::render('Laboredge/index', [
            'jobs' => $jobs,
            'filters' => $filters,
            'statuses' => Laboredge::distinct()->whereNotNull('status')->pluck('status'),
            'professions' => Laboredge::distinct()->whereNotNull('profession')->pluck('profession'),
        ]);
    }

    public function candidates(Request $request): Response
    {
        $filters = $request->only(['search', 'status', 'profession']);

        $candidates = VmsCandidate::query()
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('name', 'ilike', "%{$search}%")
                        ->orWhere('email', 'ilike', "%{$search}%")
                        ->orWhere('phone', 'ilike', "%{$search}%")
                        ->orWhere('state', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['status'] ?? null, function ($query, $status) {
                $query->where('status', $status);
            })
            ->when($filters['profession'] ?? null, function ($query, $profession) {
                $query->where('profession', $profession);
            })
            ->orderBy('last_updated', 'desc')
            ->paginate(15)
            ->withQueryString();

        return Inertia::render('Laboredge/Candidates', [
            'candidates' => $candidates,
            'filters' => $filters,
            'statuses' => VmsCandidate::distinct()->whereNotNull('status')->pluck('status'),
            'professions' => VmsCandidate::distinct()->whereNotNull('profession')->pluck('profession'),
        ]);
    }
}
