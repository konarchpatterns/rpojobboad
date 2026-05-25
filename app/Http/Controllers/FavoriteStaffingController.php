<?php

namespace App\Http\Controllers;

use App\Models\FavoriteStaffing;
use App\Models\FmsCandidate;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class FavoriteStaffingController extends Controller
{
    public function index(Request $request): Response
    {
        $filters = $request->only(['search', 'status', 'job_class']);

        $jobs = FavoriteStaffing::query()
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('job_class', 'ilike', "%{$search}%")
                        ->orWhere('location', 'ilike', "%{$search}%")
                        ->orWhere('order_id', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['status'] ?? null, function ($query, $status) {
                $query->where('status', $status);
            })
            ->when($filters['job_class'] ?? null, function ($query, $job_class) {
                $query->where('job_class', $job_class);
            })
            ->orderBy('last_seen', 'desc')
            ->paginate(10)
            ->withQueryString();

        return Inertia::render('FavoriteStaffing/index', [
            'jobs' => $jobs,
            'filters' => $filters,
            'statuses' => FavoriteStaffing::distinct()->whereNotNull('status')->pluck('status'),
            'job_classes' => FavoriteStaffing::distinct()->whereNotNull('job_class')->pluck('job_class'),
        ]);
    }

    public function candidates(Request $request): Response
    {
        $filters = $request->only(['search', 'status', 'job_class']);

        $candidates = FmsCandidate::query()
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('first_name', 'ilike', "%{$search}%")
                        ->orWhere('last_name', 'ilike', "%{$search}%")
                        ->orWhere('area', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['status'] ?? null, function ($query, $status) {
                $query->where('status', $status);
            })
            ->when($filters['job_class'] ?? null, function ($query, $job_class) {
                $query->where('job_class', $job_class);
            })
            ->orderBy('last_seen', 'desc')
            ->paginate(15)
            ->withQueryString();

        return Inertia::render('FavoriteStaffing/Candidates', [
            'candidates' => $candidates,
            'filters' => $filters,
            'statuses' => FmsCandidate::distinct()->whereNotNull('status')->pluck('status'),
            'job_classes' => FmsCandidate::distinct()->whereNotNull('job_class')->pluck('job_class'),
        ]);
    }
}
