<?php

namespace App\Console\Commands;

use App\Models\ScheduledTask;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Illuminate\Console\Command;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;

class RunPythonScript extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'run-python-script {script} {--task= : The ID of the scheduled task}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Run a python script and optionally update a scheduled task status';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $scriptPath = $this->argument('script');
        $taskId = $this->option('task');
        $task = $taskId ? ScheduledTask::find($taskId) : null;

        $absolutePath = base_path($scriptPath);

        if (!file_exists($absolutePath)) {
            $this->error("Script not found at: {$absolutePath}");
            if ($task) {
                $task->update([
                    'status' => 'failed',
                    'last_output' => "Script not found at: {$absolutePath}",
                    'last_run_at' => now(),
                ]);
            }
            return 1;
        }

        $this->info("Running Python script: {$absolutePath}");

        if ($task) {
            // If the task status is no longer 'pending', it means it was stopped while in the queue.
            if ($task->status !== 'pending') {
                $this->info("Task #{$task->id} was cancelled or stopped before starting. Skipping.");
                return 0;
            }

            $task->update([
                'status' => 'running',
                'last_run_at' => now(),
            ]);
        }

        // Use 'python' or 'python3' depending on the environment. 
        // On Windows it's usually 'python'.
        $process = new Process(['python', $absolutePath]);
        $process->setTimeout(3600); // 1 hour timeout for scrapers

        try {
            $process->start();

            if ($task) {
                $task->update(['pid' => $process->getPid()]);
            }

            foreach ($process as $type => $buffer) {
                $this->output->write($buffer);
            }

            $process->wait();

            $output = $process->getOutput() . "\n" . $process->getErrorOutput();
            $status = $process->isSuccessful() ? 'success' : 'failed';

            if ($task) {
                $task->update([
                    'status' => $status,
                    'last_output' => $output,
                    'pid' => null,
                ]);
            }

            if (!$process->isSuccessful()) {
                $this->error("Process failed with exit code: " . $process->getExitCode());
                return 1;
            }

            $this->info("Python script completed successfully.");
            return 0;

        } catch (\Exception $e) {
            $this->error("An error occurred: " . $e->getMessage());
            if ($task) {
                $task->update([
                    'status' => 'failed',
                    'last_output' => $e->getMessage(),
                ]);
            }
            return 1;
        }
    }
}
