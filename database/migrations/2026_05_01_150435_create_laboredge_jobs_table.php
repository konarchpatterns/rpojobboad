<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('laboredge_jobs', function (Blueprint $table) {
            $table->id();
            $table->string('job_id', 50)->unique();
            $table->text('status')->nullable();
            $table->text('facility')->nullable();
            $table->text('state')->nullable();
            $table->text('job_type')->nullable();
            $table->text('profession')->nullable();
            $table->text('specialty')->nullable();
            $table->text('shift')->nullable();
            $table->text('start_date')->nullable();
            $table->text('posted_on')->nullable();
            $table->text('city')->nullable();
            $table->timestamp('last_seen')->useCurrent();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('laboredge_jobs');
    }
};
