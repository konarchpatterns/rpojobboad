<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Fieldglass extends Model
{
    /** @use HasFactory<\Database\Factories\FieldglassFactory> */
    use HasFactory;

    protected $table = 'fieldglass_jobs';

    protected $fillable = [
        'job_id',
        'title',
        'status',
        'bill_rate',
        'site',
        'updated_at',
    ];

    protected $casts = [
        'updated_at' => 'datetime',
    ];
}
