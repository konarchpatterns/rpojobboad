<?php

namespace App\Http\Controllers;

use App\Models\MedefisJob;
use App\Models\MedefisCandidate;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class MedefisController extends Controller
{
    public function index(Request $request): Response
    {
        $filters = $request->only(['search', 'specialty', 'facility']);

        $jobs = MedefisJob::query()
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('job_name', 'ilike', "%{$search}%")
                        ->orWhere('facility', 'ilike', "%{$search}%")
                        ->orWhere('job_number', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['specialty'] ?? null, function ($query, $specialty) {
                $query->where('specialty', $specialty);
            })
            ->when($filters['facility'] ?? null, function ($query, $facility) {
                $query->where('facility', $facility);
            })
            ->orderBy('posted_date', 'desc')
            ->paginate(10)
            ->withQueryString();

        return Inertia::render('Medefis/index', [
            'jobs' => $jobs,
            'filters' => $filters,
            'specialties' => MedefisJob::distinct()->whereNotNull('specialty')->pluck('specialty'),
            'facilities' => MedefisJob::distinct()->whereNotNull('facility')->pluck('facility'),
        ]);
    }

    public function candidates(Request $request): Response
    {
        $filters = $request->only(['search', 'state', 'specialty']);

        $candidates = MedefisCandidate::query()
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('candidate_name', 'ilike', "%{$search}%")
                        ->orWhere('email', 'ilike', "%{$search}%")
                        ->orWhere('candidate_id', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['state'] ?? null, function ($query, $state) {
                $query->where('state', $state);
            })
            ->when($filters['specialty'] ?? null, function ($query, $specialty) {
                $query->where('specialty', $specialty);
            })
            ->orderBy('last_updated', 'desc')
            ->paginate(15)
            ->withQueryString();

        return Inertia::render('Medefis/Candidates', [
            'candidates' => $candidates,
            'filters' => $filters,
            'states' => MedefisCandidate::distinct()->whereNotNull('state')->pluck('state'),
            'specialties' => MedefisCandidate::distinct()->whereNotNull('specialty')->pluck('specialty'),
        ]);
    }
}
