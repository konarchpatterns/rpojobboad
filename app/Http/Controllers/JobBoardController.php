<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Inertia\Inertia;
use App\Models\Bluesky;
use App\Models\FavoriteStaffing;
use App\Models\Fieldglass;
use App\Models\Hwl;
use App\Models\Laboredge;
use App\Models\MedefisJob;
use App\Models\SaintFrancisJob;
use App\Models\Trovms;
use App\Models\Westway;

use App\Traits\UnifiedJobQuery;
use App\Traits\UnifiedCandidateQuery;

class JobBoardController extends Controller
{
    use UnifiedJobQuery, UnifiedCandidateQuery;

    public function index(Request $request)
    {
        $search = $request->input('search');
        $portalFilter = $request->input('portal');

        $jobs = $this->getUnifiedJobsQuery($search, $portalFilter)
            ->paginate(50)
            ->withQueryString();

        return Inertia::render('AllJobs', [
            'jobs' => $jobs,
            'filters' => $request->only(['search', 'portal'])
        ]);
    }

    public function show(string $portal, string $id)
    {
        $jobData = null;

        switch ($portal) {
            case 'Bluesky':
                $jobData = Bluesky::where('job_id', $id)->firstOrFail();
                break;
            case 'Favorite Staffing':
                $jobData = FavoriteStaffing::where('order_id', $id)->firstOrFail();
                break;
            case 'Fieldglass':
                $jobData = Fieldglass::where('job_id', $id)->firstOrFail();
                break;
            case 'HWL':
                $jobData = Hwl::with('details')->where('job_id', $id)->firstOrFail();
                break;
            case 'Laboredge':
                $jobData = Laboredge::with('details')->where('job_id', $id)->firstOrFail();
                break;
            case 'Medefis':
                $jobData = MedefisJob::where('job_number', $id)->firstOrFail();
                break;
            case 'Saint Francis':
                $jobData = SaintFrancisJob::where('job_id', $id)->firstOrFail();
                break;
            case 'Trovms':
                $jobData = Trovms::where('job_id', $id)->firstOrFail();
                break;
            case 'Westway':
                $jobData = Westway::with('detail')->where('job_id', $id)->firstOrFail();
                break;
            default:
                abort(404, 'Portal not found');
        }

        return Inertia::render('JobDetails', [
            'job' => $jobData,
            'portal' => $portal
        ]);
    }

    public function allCandidates(Request $request)
    {
        $search = $request->input('search');
        $portalFilter = $request->input('portal');

        $candidates = $this->getUnifiedCandidatesQuery($search, $portalFilter)
            ->orderBy('last_updated', 'desc')
            ->paginate(50)
            ->withQueryString();

        return Inertia::render('AllCandidates', [
            'candidates' => $candidates,
            'filters' => $request->only(['search', 'portal']),
            'portals' => ['Westway', 'National Staffing', 'Favourite Staffing', 'HWLMSP', 'AHSA', 'RS Primary', 'Medefis']
        ]);
    }
}
