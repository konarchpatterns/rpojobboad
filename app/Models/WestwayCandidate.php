<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class WestwayCandidate extends Model
{
    /** @use HasFactory<\Database\Factories\WestwayCandidateFactory> */
    use HasFactory;

    public $timestamps = false;

    protected $fillable = [
        'appl_id',
        'company_id',
        'company_name',
        'status',
        'first_name',
        'last_name',
        'mi',
        'ssn',
        'city',
        'email',
        'home_phone',
        'cell_phone',
        'date_available',
        'last_updated',
    ];

    protected $casts = [
        'last_updated' => 'datetime',
    ];
}
