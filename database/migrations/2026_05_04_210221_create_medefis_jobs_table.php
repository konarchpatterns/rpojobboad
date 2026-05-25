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
        Schema::create('medefis_jobs', function (Blueprint $table) {
            $table->id();
            $table->string('job_number', 50)->unique();
            $table->text('job_name')->nullable();
            $table->text('facility')->nullable();
            $table->text('specialty')->nullable();
            $table->text('sub_specialty')->nullable();
            $table->text('job_type')->nullable();
            $table->text('positions')->nullable();
            $table->text('start_date')->nullable();
            $table->text('posted_date')->nullable();
            $table->text('last_updated')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('medefis_jobs');
    }
};
