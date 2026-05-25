<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

use App\Models\ScheduledTask;

class ScheduledTaskSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $tasks = [
            [
                'name' => 'Westway: Job Scraper',
                'command' => 'storage/app/python/westway/data.py',
                'expression' => '0 0 * * *',
            ],
            [
                'name' => 'Westway: Candidate Scraper',
                'command' => 'storage/app/python/westway/candidate.py',
                'expression' => '0 1 * * *',
            ],
            [
                'name' => 'HWL: Job Scraper',
                'command' => 'storage/app/python/hwl/data.py',
                'expression' => '0 2 * * *',
            ],
            [
                'name' => 'HWL: Candidate Scraper',
                'command' => 'storage/app/python/hwl/candidate.py',
                'expression' => '0 3 * * *',
            ],
            [
                'name' => 'Medefis: Job Scraper',
                'command' => 'storage/app/python/medfis/scrap.py',
                'expression' => '0 4 * * *',
            ],
            [
                'name' => 'RS Primary: Candidate Scraper',
                'command' => 'storage/app/python/rsprimary/candidate.py',
                'expression' => '0 5 * * *',
            ],
            [
                'name' => 'TrioVMS: Job Scraper',
                'command' => 'storage/app/python/triovms/data.py',
                'expression' => '0 6 * * *',
            ],
        ];

        foreach ($tasks as $task) {
            ScheduledTask::updateOrCreate(
                ['command' => $task['command']],
                [
                    'name' => $task['name'],
                    'expression' => $task['expression'],
                    'is_active' => true,
                    'status' => 'idle',
                ]
            );
        }
    }
}
