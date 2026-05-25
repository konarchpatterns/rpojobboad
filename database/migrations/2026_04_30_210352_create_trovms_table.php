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
        Schema::create('trovms', function (Blueprint $table) {
            $table->id();
            $table->integer('job_id')->unique();
            $table->text('bid_due_date')->nullable();
            $table->string('city', 100)->nullable();
            $table->text('facility')->nullable();
            $table->string('profession', 100)->nullable();
            $table->string('reason', 100)->nullable();
            $table->string('specialty', 150)->nullable();
            $table->string('start_date')->nullable();
            $table->string('state', 2)->nullable();
            $table->string('status', 50)->nullable();
            $table->string('job_type', 50)->nullable();
            $table->timestamp('last_updated')->useCurrent();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('trovms');
    }
};
