<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class TrovmsCandidate extends Model
{
    /** @use HasFactory<\Database\Factories\TrovmsCandidateFactory> */
    use HasFactory;

    public $timestamps = false;

    protected $fillable = [
        'candidate_number',
        'candidate_uuid',
        'name',
        'npi',
        'phone',
        'email',
        'years_exp',
        'travel_exp',
        'selling_points',
        'last_updated',
    ];

    protected $casts = [
        'last_updated' => 'datetime',
    ];
}
