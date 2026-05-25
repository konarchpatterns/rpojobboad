<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class VmsCandidate extends Model
{
    /** @use HasFactory<\Database\Factories\VmsCandidateFactory> */
    use HasFactory;

    protected $table = 'vms_candidates';
    public $timestamps = false;

    protected $fillable = [
        'name',
        'email',
        'phone',
        'state',
        'status',
        'profession',
        'specialty',
        'last_updated',
    ];

    protected $casts = [
        'last_updated' => 'datetime',
    ];
}
