<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SaintFrancisJob extends Model
{
    use HasFactory;

    protected $table = 'saint_francis_jobs';

    protected $fillable = [
        'job_id',
        'position',
        'status',
        'applicants',
        'pay_rate',
        'location',
        'last_updated',
    ];

    protected $casts = [
        'last_updated' => 'datetime',
    ];
}
