<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class LaboredgeDetail extends Model
{
    protected $table = 'laboredge_job_details';

    protected $fillable = [
        'job_id',
        'facility',
        'status',
        'profession',
        'specialty',
        'start_date',
        'end_date',
        'bill_rate',
        'description',
        'scraped_at',
    ];

    protected $casts = [
        'scraped_at' => 'datetime',
    ];

    public function laboredge()
    {
        return $this->belongsTo(Laboredge::class, 'job_id', 'job_id');
    }
}
