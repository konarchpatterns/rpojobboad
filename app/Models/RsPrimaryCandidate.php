<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class RsPrimaryCandidate extends Model
{
    /** @use HasFactory<\Database\Factories\RsPrimaryCandidateFactory> */
    use HasFactory;

    public $timestamps = false;
    protected $table = 'rsprimary_candidates';

    protected $fillable = [
        'unique_id',
        'name',
        'first_name',
        'last_name',
        'email',
        'phone',
        'address',
        'vendor',
        'experience',
        'bill_rate',
        'ssn_last_4',
        'skills',
        'profile_url',
        'last_updated',
    ];

    protected $casts = [
        'last_updated' => 'datetime',
    ];
}
