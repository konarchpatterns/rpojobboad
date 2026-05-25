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
        Schema::create('fieldglass_jobs', function (Blueprint $table) {
            $table->id();
            $table->string('job_id', 50)->unique();
            $table->text('title')->nullable();
            $table->text('status')->nullable();
            $table->text('bill_rate')->nullable();
            $table->text('site')->nullable();
            $table->timestamp('updated_at')->useCurrent();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('fieldglass_jobs');
    }
};
