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
        Schema::create('bluesky_jobs', function (Blueprint $table) {
            $table->id();
            $table->string('job_id', 50)->unique();
            $table->text('facility')->nullable();
            $table->text('unit')->nullable();
            $table->text('start_date')->nullable();
            $table->text('end_date')->nullable();
            $table->text('duration')->nullable();
            $table->text('shift')->nullable();
            $table->text('profession')->nullable();
            $table->text('city')->nullable();
            $table->text('state')->nullable();
            $table->text('pay_rate')->nullable();
            $table->text('description')->nullable();
            $table->timestamp('last_seen')->useCurrent();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('bluesky_jobs');
    }
};
