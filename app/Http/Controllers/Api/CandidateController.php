<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Traits\UnifiedCandidateQuery;

class CandidateController extends Controller
{
    use UnifiedCandidateQuery;

    public function index(Request $request)
    {
        $search = $request->input('search');
        $portalFilter = $request->input('portal');

        $candidates = $this->getUnifiedCandidatesQuery($search, $portalFilter)
            ->orderBy('last_updated', 'desc')
            ->paginate(50);

        $grouped = collect($candidates->items())->groupBy('portal');
        $enrichedCandidates = [];

        foreach ($grouped as $portal => $items) {
            $ids = $items->pluck('id')->toArray();
            $models = collect();

            switch ($portal) {
                case 'Westway':
                    $models = \App\Models\WestwayCandidate::whereIn('id', $ids)->get()->keyBy('id');
                    break;
                case 'National Staffing':
                    $models = \App\Models\VmsCandidate::whereIn('id', $ids)->get()->keyBy('id');
                    break;
                case 'Favourite Staffing':
                    $models = \App\Models\FmsCandidate::whereIn('id', $ids)->get()->keyBy('id');
                    break;
                case 'HWLMSP':
                    $models = \App\Models\HwlCandidate::whereIn('id', $ids)->get()->keyBy('id');
                    break;
                case 'AHSA':
                    $models = \App\Models\TrovmsCandidate::whereIn('id', $ids)->get()->keyBy('id');
                    break;
                case 'RS Primary':
                    $models = \App\Models\RsPrimaryCandidate::whereIn('unique_id', $ids)->get()->keyBy('unique_id');
                    break;
                case 'Medefis':
                    $models = \App\Models\MedefisCandidate::whereIn('candidate_id', $ids)->get()->keyBy('candidate_id');
                    break;
            }

            foreach ($items as $item) {
                // Determine the correct key to check based on portal
                $keyField = ($portal === 'RS Primary') ? 'unique_id' : 'id';
                
                if ($models->has($item->id)) {
                    $enriched = $models->get($item->id)->toArray();
                    $enriched['portal'] = $portal;
                    $enrichedCandidates[$portal . '_' . $item->id] = $enriched;
                }
            }
        }

        $finalItems = collect($candidates->items())->map(function($item) use ($enrichedCandidates) {
            $key = $item->portal . '_' . $item->id;
            return $enrichedCandidates[$key] ?? $item;
        });

        $candidates->setCollection($finalItems);

        return response()->json($candidates);
    }
}
