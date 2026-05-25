<?php

namespace App\Traits;

use Illuminate\Support\Facades\DB;

trait UnifiedCandidateQuery
{
    protected function getUnifiedCandidatesQuery($search = null, $portalFilter = null)
    {
        $westway = DB::table('westway_candidates')
            ->select(
                DB::raw('CAST(westway_candidates.id AS TEXT) as id'),
                DB::raw("CONCAT(first_name, ' ', last_name) as name"),
                'email',
                'cell_phone as phone',
                DB::raw("'Westway' as portal"),
                'last_updated'
            );

        $laboredge = DB::table('vms_candidates')
            ->select(DB::raw('CAST(vms_candidates.id AS TEXT) as id'), 'name', 'email', 'phone', DB::raw("'National Staffing' as portal"), 'last_updated');

        $fms = DB::table('fms_candidates')
            ->select(
                DB::raw('CAST(fms_candidates.id AS TEXT) as id'),
                DB::raw("CONCAT(first_name, ' ', last_name) as name"),
                DB::raw("'' as email"),
                DB::raw("'' as phone"),
                DB::raw("'Favourite Staffing' as portal"),
                DB::raw("last_seen as last_updated")
            );

        $hwl = DB::table('hwl_candidates')
            ->select(
                DB::raw('CAST(hwl_candidates.id AS TEXT) as id'),
                DB::raw("CONCAT(first_name, ' ', last_name) as name"),
                'email',
                DB::raw("mobile as phone"),
                DB::raw("'HWLMSP' as portal"),
                'last_updated'
            );

        $asha = DB::table('trovms_candidates')
            ->select(DB::raw('CAST(trovms_candidates.id AS TEXT) as id'), 'name', 'email', 'phone', DB::raw("'AHSA' as portal"), 'last_updated');

        $rsprimary = DB::table('rsprimary_candidates')
            ->select(DB::raw('CAST(rsprimary_candidates.unique_id AS TEXT) as id'), 'name', 'email', 'phone', DB::raw("'RS Primary' as portal"), 'last_updated');

        $medefis = DB::table('medefis_candidates')
            ->select(
                DB::raw('CAST(medefis_candidates.candidate_id AS TEXT) as id'),
                DB::raw('candidate_name as name'),
                'email',
                DB::raw("'' as phone"),
                DB::raw("'Medefis' as portal"),
                'last_updated'
            );

        $combined = $westway
            ->unionAll($laboredge)
            ->unionAll($fms)
            ->unionAll($hwl)
            ->unionAll($asha)
            ->unionAll($rsprimary)
            ->unionAll($medefis);

        $query = DB::table(DB::raw("({$combined->toSql()}) as combined_candidates"))
            ->mergeBindings($combined);

        if ($portalFilter && $portalFilter !== 'All') {
            $query->where('portal', $portalFilter);
        }

        if ($search) {
            $query->where(function($q) use ($search) {
                $q->where('name', 'ILIKE', "%{$search}%")
                  ->orWhere('email', 'ILIKE', "%{$search}%")
                  ->orWhere('phone', 'ILIKE', "%{$search}%");
            });
        }

        return $query;
    }
}
