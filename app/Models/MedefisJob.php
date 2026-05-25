<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class MedefisJob extends Model
{
    use HasFactory;

    protected $table = 'medefis_jobs';

    protected $fillable = [
        'job_name',
        'job_number',
        'facility',
        'specialty',
        'sub_specialty',
        'job_type',
        'positions',
        'start_date',
        'posted_date',
        'details_json',
        'last_updated',
    ];

    protected $casts = [
        'details_json' => 'array',
    ];

}
