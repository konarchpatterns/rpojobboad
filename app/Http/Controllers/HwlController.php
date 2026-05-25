<?php

namespace App\Http\Controllers;

use App\Models\Hwl;
use App\Models\HwlCandidate;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class HwlController extends Controller
{
    public function index(Request $request): Response
    {
        $filters = $request->only(['search', 'specialty', 'facility']);

        $jobs = Hwl::query()
            ->with('details')
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('job_title', 'ilike', "%{$search}%")
                        ->orWhere('facility', 'ilike', "%{$search}%")
                        ->orWhere('job_id', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['specialty'] ?? null, function ($query, $specialty) {
                $query->where('specialty', $specialty);
            })
            ->when($filters['facility'] ?? null, function ($query, $facility) {
                $query->where('facility', $facility);
            })
            ->orderBy('last_updated', 'desc')
            ->paginate(10)
            ->withQueryString();

        return Inertia::render('Hwl/index', [
            'jobs' => $jobs,
            'filters' => $filters,
            'specialties' => Hwl::distinct()->whereNotNull('specialty')->pluck('specialty'),
            'facilities' => Hwl::distinct()->whereNotNull('facility')->pluck('facility'),
        ]);
    }

    public function candidates(Request $request): Response
    {
        $filters = $request->only(['search', 'gender', 'state']);

        $candidates = HwlCandidate::query()
            ->when($filters['search'] ?? null, function ($query, $search) {
                $query->where(function ($query) use ($search) {
                    $query->where('first_name', 'ilike', "%{$search}%")
                        ->orWhere('last_name', 'ilike', "%{$search}%")
                        ->orWhere('email', 'ilike', "%{$search}%")
                        ->orWhere('profile_id', 'ilike', "%{$search}%");
                });
            })
            ->when($filters['gender'] ?? null, function ($query, $gender) {
                $query->where('gender', $gender);
            })
            ->when($filters['state'] ?? null, function ($query, $state) {
                $query->where('state', $state);
            })
            ->orderBy('last_updated', 'desc')
            ->paginate(15)
            ->withQueryString();

        return Inertia::render('Hwl/Candidates', [
            'candidates' => $candidates,
            'filters' => $filters,
            'genders' => HwlCandidate::distinct()->whereNotNull('gender')->pluck('gender'),
            'states' => HwlCandidate::distinct()->whereNotNull('state')->pluck('state'),
        ]);
    }
}
