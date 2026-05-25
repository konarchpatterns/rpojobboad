<?php

namespace App\Http\Controllers;

use App\Models\ScheduledTask;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Artisan;
use Inertia\Inertia;
use Cron\CronExpression;

class SchedulerController extends Controller
{
    public function index()
    {
        $tasks = ScheduledTask::orderBy('created_at', 'desc')->get();
        
        // Calculate next run for active tasks
        foreach ($tasks as $task) {
            if ($task->is_active && $task->expression) {
                try {
                    $cron = new CronExpression($task->expression);
                    $task->next_run_at = $cron->getNextRunDate()->format('Y-m-d H:i:s');
                } catch (\Exception $e) {
                    $task->next_run_at = null;
                }
            }
        }

        return Inertia::render('Scheduler/Index', [
            'tasks' => $tasks
        ]);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'command' => 'required|string|max:255',
            'expression' => 'required|string|max:255',
            'is_active' => 'boolean',
        ]);

        ScheduledTask::create($validated);

        return redirect()->back()->with('message', 'Task created successfully.');
    }

    public function update(Request $request, ScheduledTask $task)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'command' => 'required|string|max:255',
            'expression' => 'required|string|max:255',
            'is_active' => 'boolean',
        ]);

        $task->update($validated);

        return redirect()->back()->with('message', 'Task updated successfully.');
    }

    public function destroy(ScheduledTask $task)
    {
        $task->delete();
        return redirect()->back()->with('message', 'Task deleted successfully.');
    }

    public function run(ScheduledTask $task)
    {
        // Run the command in the background via queue
        Artisan::queue('run-python-script', [
            'script' => $task->command,
            '--task' => $task->id,
        ]);

        $task->update(['status' => 'pending']);

        return redirect()->back()->with('message', 'Task queued for execution.');
    }

    public function stop(ScheduledTask $task)
    {
        if ($task->status === 'idle') {
            return redirect()->back()->with('error', 'Task is not running.');
        }

        if ($task->pid) {
            // On Windows, use taskkill. /F is force, /T is tree (kill children too)
            exec("taskkill /F /PID {$task->pid} /T");
        }
        
        $task->update([
            'status' => 'idle', // Reset to idle
            'pid' => null,
            'last_output' => $task->last_output . "\n\n[!] Task was manually stopped."
        ]);

        return redirect()->back()->with('message', 'Task stopped successfully.');
    }
}
