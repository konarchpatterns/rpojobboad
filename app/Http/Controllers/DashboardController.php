<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\SaintFrancisJob;
use App\Models\MedefisJob;
use App\Models\MedefisCandidate;
use App\Models\Trovms;
use App\Models\Bluesky;
use App\Models\Fieldglass;
use App\Models\FavoriteStaffing;
use App\Models\Laboredge;
use App\Models\Hwl;
use App\Models\Westway;
use App\Models\WestwayCandidate;
use App\Models\VmsCandidate;
use App\Models\FmsCandidate;
use App\Models\HwlCandidate;
use App\Models\TrovmsCandidate;
use App\Models\RsPrimaryCandidate;
use Inertia\Inertia;
use Inertia\Response;

class DashboardController extends Controller
{
    public function index(): Response
    {
        $trovmsCount = Trovms::count();
        $ashaCandidateCount = TrovmsCandidate::count();
        $blueskyCount = Bluesky::count();
        $fieldglassCount = Fieldglass::count();
        $favoriteStaffingCount = FavoriteStaffing::count();
        $fmsCandidateCount = FmsCandidate::count();
        $laboredgeCount = Laboredge::count();
        $vmsCandidateCount = VmsCandidate::count();
        $hwlCount = Hwl::count();
        $hwlCandidateCount = HwlCandidate::count();
        $westwayCount = Westway::count();
        $westwayCandidateCount = WestwayCandidate::count();
        $medefisCount = MedefisJob::count();
        $medefisCandidateCount = MedefisCandidate::count();
        $saintFrancisCount = SaintFrancisJob::count();
        $rsPrimaryCandidateCount = RsPrimaryCandidate::count();

        return Inertia::render('Dashboard', [
            'trovmsCount' => $trovmsCount,
            'ashaCandidateCount' => $ashaCandidateCount,
            'blueskyCount' => $blueskyCount,
            'fieldglassCount' => $fieldglassCount,
            'favoriteStaffingCount' => $favoriteStaffingCount,
            'fmsCandidateCount' => $fmsCandidateCount,
            'laboredgeCount' => $laboredgeCount,
            'vmsCandidateCount' => $vmsCandidateCount,
            'hwlCount' => $hwlCount,
            'hwlCandidateCount' => $hwlCandidateCount,
            'westwayCount' => $westwayCount,
            'westwayCandidateCount' => $westwayCandidateCount,
            'medefisCount' => $medefisCount,
            'medefisCandidateCount' => $medefisCandidateCount,
            'saintFrancisCount' => $saintFrancisCount,
            'rsPrimaryCandidateCount' => $rsPrimaryCandidateCount,
        ]);
    }
}
