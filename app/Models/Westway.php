<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Westway extends Model
{
    /** @use HasFactory<\Database\Factories\WestwayFactory> */
    use HasFactory;

    protected $table = 'westway';

    protected $fillable = [
        'job_id',
        'company_id',
        'company_name',
        'status',
        'opened',
        'start_date',
        'end_date',
        'position',
        'department',
        'qty',
        'job_type',
        'last_updated',
    ];

    protected $casts = [
        'last_updated' => 'datetime',
    ];

    public function detail()
    {
        return $this->hasOne(WestwayDetail::class, 'job_id', 'job_id');
    }
}
