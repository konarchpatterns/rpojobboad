<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Hwl extends Model
{
    use HasFactory;

    protected $table = 'hwl';

    protected $fillable = [
        'job_id',
        'facility',
        'job_title',
        'specialty',
        'last_updated',
    ];

    protected $casts = [
        'last_updated' => 'datetime',
    ];

    public function details()
    {
        return $this->hasOne(HwlDetail::class, 'job_id', 'job_id');
    }
}
