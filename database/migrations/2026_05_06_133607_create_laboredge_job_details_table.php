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
        Schema::create('laboredge_job_details', function (Blueprint $table) {
            $table->id();
            $table->string('job_id', 50)->unique();
            $table->text('facility')->nullable();
            $table->text('status')->nullable();
            $table->text('profession')->nullable();
            $table->text('specialty')->nullable();
            $table->text('start_date')->nullable();
            $table->text('end_date')->nullable();
            $table->text('bill_rate')->nullable();
            $table->text('description')->nullable();
            $table->timestamp('scraped_at')->useCurrent();
            $table->timestamps();

            $table->foreign('job_id')->references('job_id')->on('laboredge_jobs')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('laboredge_job_details');
    }
};
