<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class HwlDetail extends Model
{
    use HasFactory;

    protected $table = 'hwl_details';

    protected $fillable = [
        'job_id',
        'address',
        'shift',
        'weeks',
        'pay_rates',
        'last_updated',
    ];

    protected $casts = [
        'pay_rates' => 'array',
        'last_updated' => 'datetime',
    ];

    public function hwl()
    {
        return $this->belongsTo(Hwl::class, 'job_id', 'job_id');
    }
}
