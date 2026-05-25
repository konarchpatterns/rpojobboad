<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Traits\UnifiedJobQuery;
use App\Models\Bluesky;
use App\Models\FavoriteStaffing;
use App\Models\Fieldglass;
use App\Models\Hwl;
use App\Models\Laboredge;
use App\Models\MedefisJob;
use App\Models\SaintFrancisJob;
use App\Models\Trovms;
use App\Models\Westway;

class JobController extends Controller
{
    use UnifiedJobQuery;

    public function index(Request $request)
    {
        $search = $request->input('search');
        $portalFilter = $request->input('portal');

        $jobs = $this->getUnifiedJobsQuery($search, $portalFilter)
            ->paginate(50);

        // Group by portal to efficiently fetch full models
        $grouped = collect($jobs->items())->groupBy('portal');
        $enrichedJobs = [];

        foreach ($grouped as $portal => $items) {
            $ids = $items->pluck('job_id')->toArray();
            $models = collect();

            switch ($portal) {
                case 'Bluesky':
                    $models = Bluesky::whereIn('job_id', $ids)->get()->keyBy('job_id');
                    break;
                case 'Favorite Staffing':
                    $models = FavoriteStaffing::whereIn('order_id', $ids)->get()->keyBy('order_id');
                    break;
                case 'Fieldglass':
                    $models = Fieldglass::whereIn('job_id', $ids)->get()->keyBy('job_id');
                    break;
                case 'HWL':
                    $models = Hwl::with('details')->whereIn('job_id', $ids)->get()->keyBy('job_id');
                    break;
                case 'Laboredge':
                    $models = Laboredge::with('details')->whereIn('job_id', $ids)->get()->keyBy('job_id');
                    break;
                case 'Medefis':
                    $models = MedefisJob::whereIn('job_number', $ids)->get()->keyBy('job_number');
                    break;
                case 'Saint Francis':
                    $models = SaintFrancisJob::whereIn('job_id', $ids)->get()->keyBy('job_id');
                    break;
                case 'Trovms':
                    $models = Trovms::whereIn('job_id', $ids)->get()->keyBy('job_id');
                    break;
                case 'Westway':
                    $models = Westway::with('detail')->whereIn('job_id', $ids)->get()->keyBy('job_id');
                    break;
            }

            foreach ($items as $item) {
                if ($models->has($item->job_id)) {
                    $enriched = $models->get($item->job_id)->toArray();
                    $enriched['portal'] = $portal; // Re-inject portal name
                    $enrichedJobs[$portal . '_' . $item->job_id] = $enriched;
                }
            }
        }

        // Map back to original order with enriched data
        $finalItems = collect($jobs->items())->map(function($item) use ($enrichedJobs) {
            $key = $item->portal . '_' . $item->job_id;
            return $enrichedJobs[$key] ?? $item;
        });

        // Replace the collection in the paginator
        $jobs->setCollection($finalItems);

        return response()->json($jobs);
    }

    public function show(string $portal, string $id)
    {
        $jobData = null;

        try {
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
                    return response()->json(['error' => 'Portal not found'], 404);
            }

            return response()->json($jobData);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Job not found'], 404);
        }
    }
}
