<?php

namespace App\Http\Controllers;

use App\Models\SaintFrancisJob;
use App\Models\RsPrimaryCandidate;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class SaintFrancisController extends Controller
{
    public function index(Request $request): Response
    {
        $filters = $request->only(['search', 'status', 'location']);

        $jobs = SaintFrancisJob::query()
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('position', 'ilike', "%{$search}%")
                        ->orWhere('location', 'ilike', "%{$search}%")
                        ->orWhere('job_id', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['status'] ?? null, function ($query, $status) {
                $query->where('status', $status);
            })
            ->when($filters['location'] ?? null, function ($query, $location) {
                $query->where('location', $location);
            })
            ->orderBy('last_updated', 'desc')
            ->paginate(10)
            ->withQueryString();

        return Inertia::render('SaintFrancis/index', [
            'jobs' => $jobs,
            'filters' => $filters,
            'statuses' => SaintFrancisJob::distinct()->whereNotNull('status')->pluck('status'),
            'locations' => SaintFrancisJob::distinct()->whereNotNull('location')->pluck('location'),
        ]);
    }

    public function candidates(Request $request): Response
    {
        $filters = $request->only(['search', 'vendor']);

        $candidates = RsPrimaryCandidate::query()
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('name', 'ilike', "%{$search}%")
                        ->orWhere('email', 'ilike', "%{$search}%")
                        ->orWhere('unique_id', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['vendor'] ?? null, function ($query, $vendor) {
                $query->where('vendor', $vendor);
            })
            ->orderBy('last_updated', 'desc')
            ->paginate(15)
            ->withQueryString();

        return Inertia::render('SaintFrancis/Candidates', [
            'candidates' => $candidates,
            'filters' => $filters,
            'vendors' => RsPrimaryCandidate::distinct()->whereNotNull('vendor')->pluck('vendor'),
        ]);
    }
}
