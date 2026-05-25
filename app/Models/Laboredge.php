<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Laboredge extends Model
{
    use HasFactory;

    protected $table = 'laboredge_jobs';

    protected $fillable = [
        'job_id',
        'status',
        'facility',
        'state',
        'job_type',
        'profession',
        'specialty',
        'shift',
        'start_date',
        'posted_on',
        'city',
        'last_seen',
    ];

    protected $casts = [
        'last_seen' => 'datetime',
    ];

    public function details()
    {
        return $this->hasOne(LaboredgeDetail::class, 'job_id', 'job_id');
    }
}
