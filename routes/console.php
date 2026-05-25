<?php

use Illuminate\Foundation\Inspiring;
use Illuminate\Support\Facades\Schedule;
use App\Models\ScheduledTask;
use Illuminate\Support\Facades\Schema;

Artisan::command('inspire', function () {
    $this->comment(Inspiring::quote());
})->purpose('Display an inspiring quote');

// Dynamic scheduling from database
if (Schema::hasTable('scheduled_tasks')) {
    $tasks = ScheduledTask::where('is_active', true)->get();
    foreach ($tasks as $task) {
        Schedule::command('run-python-script', [
            'script' => $task->command,
            '--task' => $task->id,
        ])->cron($task->expression)->appendOutputTo(storage_path('logs/scheduler.log'));
    }
}
