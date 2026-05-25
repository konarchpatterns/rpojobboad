<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class HwlCandidate extends Model
{
    /** @use HasFactory<\Database\Factories\HwlCandidateFactory> */
    use HasFactory;

    public $timestamps = false;

    protected $fillable = [
        'profile_id',
        'first_name',
        'middle_name',
        'last_name',
        'dob',
        'gender',
        'email',
        'mobile',
        'address_1',
        'city',
        'state',
        'zip_code',
        'dist_pref',
        'last_updated',
    ];

    protected $casts = [
        'last_updated' => 'datetime',
    ];
}
