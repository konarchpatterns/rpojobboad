<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class WestwayDetail extends Model
{
    protected $table = 'westway_details';

    protected $fillable = [
        'job_id',
        'position',
        'status',
        'pay_range',
        'opened',
        'dates',
        'shift_info',
        'description',
        'company_name',
        'last_updated',
    ];

    protected $casts = [
        'last_updated' => 'datetime',
    ];

    public function westway()
    {
        return $this->belongsTo(Westway::class, 'job_id', 'job_id');
    }
}
