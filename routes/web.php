<?php

use App\Http\Controllers\TrovmsController;
use App\Http\Controllers\BlueskyController;
use App\Http\Controllers\FieldglassController;
use App\Http\Controllers\SaintFrancisController;
use App\Http\Controllers\MedefisController;
use App\Http\Controllers\FavoriteStaffingController;
use App\Http\Controllers\LaboredgeController;
use App\Http\Controllers\HwlController;
use App\Http\Controllers\WestwayController;
use App\Http\Controllers\SchedulerController;
use App\Http\Controllers\ProfileController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\JobBoardController;
use Illuminate\Foundation\Application;
use Illuminate\Support\Facades\Route;
use Inertia\Inertia;

Route::get('/', function () {
    return Inertia::render('Welcome', [
        'canLogin' => Route::has('login'),
        'canRegister' => Route::has('register'),
        'laravelVersion' => Application::VERSION,
        'phpVersion' => PHP_VERSION,
    ]);
});

Route::get('/westway', [WestwayController::class, 'index'])
    ->middleware(['auth', 'verified'])
    ->name('westway.index');

Route::get('/westway/candidates', [WestwayController::class, 'candidates'])
    ->middleware(['auth', 'verified'])
    ->name('westway.candidates');

Route::get('/fieldglass', [FieldglassController::class, 'index'])
    ->middleware(['auth', 'verified'])
    ->name('fieldglass.index');

Route::get('/trovms', [TrovmsController::class, 'index'])
    ->middleware(['auth', 'verified'])
    ->name('trovms.index');

Route::get('/trovms/candidates', [TrovmsController::class, 'candidates'])
    ->middleware(['auth', 'verified'])
    ->name('trovms.candidates');

Route::get('/bluesky', [BlueskyController::class, 'index'])
    ->middleware(['auth', 'verified'])
    ->name('bluesky.index');

Route::get('/hwl', [HwlController::class, 'index'])
    ->middleware(['auth', 'verified'])
    ->name('hwl.index');

Route::get('/hwl/candidates', [HwlController::class, 'candidates'])
    ->middleware(['auth', 'verified'])
    ->name('hwl.candidates');

Route::get('/laboredge', [LaboredgeController::class, 'index'])
    ->middleware(['auth', 'verified'])
    ->name('laboredge.index');

Route::get('/laboredge/candidates', [LaboredgeController::class, 'candidates'])
    ->middleware(['auth', 'verified'])
    ->name('laboredge.candidates');

Route::get('/favorite-staffing', [FavoriteStaffingController::class, 'index'])
    ->middleware(['auth', 'verified'])
    ->name('favorite-staffing.index');

Route::get('/favorite-staffing/candidates', [FavoriteStaffingController::class, 'candidates'])
    ->middleware(['auth', 'verified'])
    ->name('favorite-staffing.candidates');

Route::get('/medefis', [MedefisController::class, 'index'])
    ->middleware(['auth', 'verified'])
    ->name('medefis.index');

Route::get('/medefis/candidates', [MedefisController::class, 'candidates'])
    ->middleware(['auth', 'verified'])
    ->name('medefis.candidates');

Route::get('/rs-primary', [SaintFrancisController::class, 'index'])
    ->middleware(['auth', 'verified'])
    ->name('saint-francis.index');

Route::get('/rs-primary/candidates', [SaintFrancisController::class, 'candidates'])
    ->middleware(['auth', 'verified'])
    ->name('saint-francis.candidates');

Route::get('/all-jobs', [JobBoardController::class, 'index'])
    ->middleware(['auth', 'verified'])
    ->name('all-jobs.index');

Route::get('/all-jobs/{portal}/{id}', [JobBoardController::class, 'show'])
    ->middleware(['auth', 'verified'])
    ->name('all-jobs.show');

Route::get('/all-candidates', [JobBoardController::class, 'allCandidates'])
    ->middleware(['auth', 'verified'])
    ->name('all-candidates.index');

Route::get('/dashboard', [DashboardController::class, 'index'])->middleware(['auth', 'verified'])->name('dashboard');

Route::middleware(['auth', 'verified'])->group(function () {
    Route::get('/scheduler', [SchedulerController::class, 'index'])->name('scheduler.index');
    Route::post('/scheduler/tasks', [SchedulerController::class, 'store'])->name('scheduler.store');
    Route::put('/scheduler/tasks/{task}', [SchedulerController::class, 'update'])->name('scheduler.update');
    Route::delete('/scheduler/tasks/{task}', [SchedulerController::class, 'destroy'])->name('scheduler.destroy');
    Route::post('/scheduler/run/{task}', [SchedulerController::class, 'run'])->name('scheduler.run');
    Route::post('/scheduler/stop/{task}', [SchedulerController::class, 'stop'])->name('scheduler.stop');
});


Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

require __DIR__.'/auth.php';
