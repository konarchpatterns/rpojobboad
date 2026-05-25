<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class FmsCandidate extends Model
{
    /** @use HasFactory<\Database\Factories\FmsCandidateFactory> */
    use HasFactory;

    protected $table = 'fms_candidates';
    public $timestamps = false;

    protected $fillable = [
        'first_name',
        'last_name',
        'job_class',
        'area',
        'status',
        'last_worked',
        'last_seen',
    ];

    protected $casts = [
        'last_seen' => 'datetime',
    ];
}
