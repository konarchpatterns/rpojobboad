<?php

namespace App\Http\Controllers;

use App\Models\Westway;
use App\Models\WestwayCandidate;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class WestwayController extends Controller
{
    public function index(Request $request): Response
    {
        $filters = $request->only(['search', 'status', 'department']);

        $jobs = Westway::query()
            ->with('detail')
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('position', 'ilike', "%{$search}%")
                        ->orWhere('company_name', 'ilike', "%{$search}%")
                        ->orWhere('job_id', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['status'] ?? null, function ($query, $status) {
                $query->where('status', $status);
            })
            ->when($filters['department'] ?? null, function ($query, $department) {
                $query->where('department', $department);
            })
            ->orderBy('last_updated', 'desc')
            ->paginate(10)
            ->withQueryString();

        return Inertia::render('Westway/Index', [
            'jobs' => $jobs,
            'filters' => $filters,
            'statuses' => Westway::distinct()->pluck('status'),
            'departments' => Westway::distinct()->pluck('department'),
        ]);
    }

    public function candidates(Request $request): Response
    {
        $filters = $request->only(['search', 'status']);

        $candidates = WestwayCandidate::query()
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('first_name', 'ilike', "%{$search}%")
                        ->orWhere('last_name', 'ilike', "%{$search}%")
                        ->orWhere('email', 'ilike', "%{$search}%")
                        ->orWhere('appl_id', 'ilike', "%{$search}%")
                        ->orWhere('company_name', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['status'] ?? null, function ($query, $status) {
                $query->where('status', $status);
            })
            ->orderBy('last_updated', 'desc')
            ->paginate(15)
            ->withQueryString();

        return Inertia::render('Westway/Candidates', [
            'candidates' => $candidates,
            'filters' => $filters,
            'statuses' => WestwayCandidate::distinct()->whereNotNull('status')->pluck('status'),
        ]);
    }
}
