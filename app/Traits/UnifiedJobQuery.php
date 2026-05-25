<?php

namespace App\Traits;

use Illuminate\Support\Facades\DB;

trait UnifiedJobQuery
{
    protected function getUnifiedJobsQuery($search = null, $portalFilter = null)
    {
        $bluesky = DB::table('bluesky_jobs')
            ->select(
                DB::raw('CAST(job_id AS TEXT) as job_id'),
                'profession as job_title',
                'facility as location',
                'city',
                'state',
                DB::raw("'N/A' as job_type"),
                DB::raw("'Bluesky' as portal"),
                DB::raw("'Active' as status"),
                'start_date',
                'end_date',
                'pay_rate'
            );

        $favorite = DB::table('favorite_staffing')
            ->select(
                DB::raw('CAST(order_id AS TEXT) as job_id'),
                'job_class as job_title',
                'location',
                DB::raw("'N/A' as city"),
                DB::raw("'N/A' as state"),
                'order_type as job_type',
                DB::raw("'Favorite Staffing' as portal"),
                'status',
                'start_date',
                'end_date',
                DB::raw("NULL as pay_rate")
            );

        $fieldglass = DB::table('fieldglass_jobs')
            ->select(
                DB::raw('CAST(job_id AS TEXT) as job_id'),
                'title as job_title',
                'site as location',
                DB::raw("'N/A' as city"),
                DB::raw("'N/A' as state"),
                DB::raw("'N/A' as job_type"),
                DB::raw("'Fieldglass' as portal"),
                'status',
                DB::raw("NULL as start_date"),
                DB::raw("NULL as end_date"),
                'bill_rate as pay_rate'
            );

        $hwl = DB::table('hwl')
            ->leftJoin('hwl_details', 'hwl.job_id', '=', 'hwl_details.job_id')
            ->select(
                DB::raw('CAST(hwl.job_id AS TEXT) as job_id'),
                'hwl.job_title',
                'hwl.facility as location',
                DB::raw("'N/A' as city"),
                DB::raw("'N/A' as state"),
                DB::raw("'N/A' as job_type"),
                DB::raw("'HWL' as portal"),
                DB::raw("'Active' as status"),
                DB::raw("NULL as start_date"),
                DB::raw("NULL as end_date"),
                DB::raw("NULL as pay_rate") // pay_rates is JSON in details, skipping for summary
            );

        $laboredge = DB::table('laboredge_jobs')
            ->leftJoin('laboredge_job_details', 'laboredge_jobs.job_id', '=', 'laboredge_job_details.job_id')
            ->select(
                DB::raw('CAST(laboredge_jobs.job_id AS TEXT) as job_id'),
                'laboredge_jobs.profession as job_title',
                'laboredge_jobs.facility as location',
                'laboredge_jobs.city',
                'laboredge_jobs.state',
                'laboredge_jobs.job_type',
                DB::raw("'Laboredge' as portal"),
                'laboredge_jobs.status',
                'laboredge_jobs.start_date',
                DB::raw("NULL as end_date"),
                'laboredge_job_details.bill_rate as pay_rate'
            );

        $medefis = DB::table('medefis_jobs')
            ->select(
                DB::raw('CAST(job_number AS TEXT) as job_id'),
                'job_name as job_title',
                'facility as location',
                DB::raw("'N/A' as city"),
                DB::raw("'N/A' as state"),
                'job_type',
                DB::raw("'Medefis' as portal"),
                DB::raw("'Active' as status"),
                'start_date',
                DB::raw("NULL as end_date"),
                DB::raw("NULL as pay_rate")
            );

        $saint_francis = DB::table('saint_francis_jobs')
            ->select(
                DB::raw('CAST(job_id AS TEXT) as job_id'),
                'position as job_title',
                'location',
                DB::raw("'N/A' as city"),
                DB::raw("'N/A' as state"),
                DB::raw("'N/A' as job_type"),
                DB::raw("'Saint Francis' as portal"),
                'status',
                DB::raw("NULL as start_date"),
                DB::raw("NULL as end_date"),
                'pay_rate'
            );

        $trovms = DB::table('trovms')
            ->select(
                DB::raw('CAST(job_id AS TEXT) as job_id'),
                'profession as job_title',
                'facility as location',
                'city',
                'state',
                'job_type',
                DB::raw("'Trovms' as portal"),
                DB::raw("'Active' as status"),
                'start_date',
                DB::raw("NULL as end_date"),
                DB::raw("NULL as pay_rate")
            );

        $westway = DB::table('westway')
            ->select(
                DB::raw('CAST(job_id AS TEXT) as job_id'),
                'position as job_title',
                'department as location',
                DB::raw("'N/A' as city"),
                DB::raw("'N/A' as state"),
                'job_type',
                DB::raw("'Westway' as portal"),
                'status',
                'start_date',
                'end_date',
                DB::raw("NULL as pay_rate")
            );

        $combined = $bluesky
            ->unionAll($favorite)
            ->unionAll($fieldglass)
            ->unionAll($hwl)
            ->unionAll($laboredge)
            ->unionAll($medefis)
            ->unionAll($saint_francis)
            ->unionAll($trovms)
            ->unionAll($westway);

        $query = DB::table(DB::raw("({$combined->toSql()}) as combined_jobs"))
            ->mergeBindings($combined);

        if ($portalFilter && $portalFilter !== 'All') {
            $query->where('portal', $portalFilter);
        }

        if ($search) {
            $query->where(function($q) use ($search) {
                $q->where('job_id', 'ILIKE', "%{$search}%")
                  ->orWhere('job_title', 'ILIKE', "%{$search}%")
                  ->orWhere('location', 'ILIKE', "%{$search}%")
                  ->orWhere('city', 'ILIKE', "%{$search}%")
                  ->orWhere('state', 'ILIKE', "%{$search}%")
                  ->orWhere('status', 'ILIKE', "%{$search}%")
                  ->orWhere('pay_rate', 'ILIKE', "%{$search}%");
            });
        }

        return $query;
    }
}
