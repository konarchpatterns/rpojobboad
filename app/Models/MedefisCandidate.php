<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class MedefisCandidate extends Model
{
    protected $table = 'medefis_candidates';
    
    protected $fillable = [
        'candidate_id',
        'candidate_name',
        'email',
        'profile_url',
        'state',
        'specialty',
        'sub_specialty',
    ];
}
