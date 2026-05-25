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
        Schema::create('saint_francis_jobs', function (Blueprint $table) {
            $table->id();
            $table->string('job_id')->unique()->nullable();
            $table->text('position')->nullable();
            $table->text('status')->nullable();
            $table->text('applicants')->nullable();
            $table->text('pay_rate')->nullable();
            $table->text('location')->nullable();
            $table->timestamp('last_updated')->useCurrent();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('saint_francis_jobs');
    }
};
