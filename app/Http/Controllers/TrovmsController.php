<?php

namespace App\Http\Controllers;

use App\Models\Trovms;
use App\Models\TrovmsCandidate;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class TrovmsController extends Controller
{
    public function index(Request $request): Response
    {
        $filters = $request->only(['search', 'status', 'profession']);

        $jobs = Trovms::query()
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('profession', 'ilike', "%{$search}%")
                        ->orWhere('facility', 'ilike', "%{$search}%")
                        ->orWhere('job_type', 'ilike', "%{$search}%")
                        ->orWhere('job_id', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['status'] ?? null, function ($query, $status) {
                $query->where('status', $status);
            })
            ->when($filters['profession'] ?? null, function ($query, $profession) {
                $query->where('profession', $profession);
            })
            ->orderBy('last_updated', 'desc')
            ->paginate(10)
            ->withQueryString();

        return Inertia::render('Trovms/index', [
            'jobs' => $jobs,
            'filters' => $filters,
            'statuses' => Trovms::distinct()->pluck('status'),
            'professions' => Trovms::distinct()->pluck('profession'),
        ]);
    }

    public function candidates(Request $request): Response
    {
        $filters = $request->only(['search', 'years_exp']);

        $candidates = TrovmsCandidate::query()
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('name', 'ilike', "%{$search}%")
                        ->orWhere('email', 'ilike', "%{$search}%")
                        ->orWhere('phone', 'ilike', "%{$search}%")
                        ->orWhere('candidate_number', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['years_exp'] ?? null, function ($query, $years_exp) {
                $query->where('years_exp', $years_exp);
            })
            ->orderBy('last_updated', 'desc')
            ->paginate(15)
            ->withQueryString();

        return Inertia::render('Trovms/Candidates', [
            'candidates' => $candidates,
            'filters' => $filters,
            'experienceLevels' => TrovmsCandidate::distinct()->whereNotNull('years_exp')->pluck('years_exp'),
        ]);
    }
}
