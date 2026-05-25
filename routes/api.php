<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\JobController;
use App\Http\Controllers\Api\CandidateController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

Route::get('/jobs', [JobController::class, 'index']);
Route::get('/jobs/{portal}/{id}', [JobController::class, 'show']);

Route::get('/candidates', [CandidateController::class, 'index']);
