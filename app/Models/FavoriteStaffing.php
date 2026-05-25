<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class FavoriteStaffing extends Model
{
    use HasFactory;

    protected $table = 'favorite_staffing';

    protected $fillable = [
        'order_id',
        'order_type',
        'status',
        'location',
        'start_date',
        'end_date',
        'shift',
        'hours',
        'job_class',
        'area',
        'last_seen',
    ];

    protected $casts = [
        'last_seen' => 'datetime',
    ];
}
