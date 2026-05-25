<?php

namespace App\Http\Controllers;

use App\Models\Fieldglass;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class FieldglassController extends Controller
{
    public function index(Request $request): Response
    {
        $filters = $request->only(['search', 'status', 'site']);

        $jobs = Fieldglass::query()
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('title', 'ilike', "%{$search}%")
                        ->orWhere('site', 'ilike', "%{$search}%")
                        ->orWhere('job_id', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['status'] ?? null, function ($query, $status) {
                $query->where('status', $status);
            })
            ->when($filters['site'] ?? null, function ($query, $site) {
                $query->where('site', $site);
            })
            ->orderBy('updated_at', 'desc')
            ->paginate(10)
            ->withQueryString();

        return Inertia::render('Fieldglass/index', [
            'jobs' => $jobs,
            'filters' => $filters,
            'statuses' => Fieldglass::distinct()->pluck('status'),
            'sites' => Fieldglass::distinct()->pluck('site'),
        ]);
    }
}
