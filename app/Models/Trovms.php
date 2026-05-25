<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Trovms extends Model
{
     use HasFactory;

    protected $table = 'trovms';

    protected $fillable = [
        'job_id',
        'bid_due_date',
        'city',
        'facility',
        'state',
        'profession',
        'reason',
        'specialty',
        'start_date',
        'status',
        'job_type',
        'description',
        'details_json',
        'last_updated'
    ];

    protected $casts = [
        'last_updated' => 'datetime',
        'details_json' => 'array',
    ];
}
