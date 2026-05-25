<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Bluesky extends Model
{
    use HasFactory;

    protected $table = 'bluesky_jobs';

    protected $fillable = [
        'job_id',
        'facility',
        'unit',
        'start_date',
        'end_date',
        'duration',
        'shift',
        'profession',
        'city',
        'state',
        'pay_rate',
        'description',
        'last_seen'
    ];

    protected $casts = [
        'last_seen' => 'datetime',
    ];
}
