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
        Schema::create('hwl', function (Blueprint $table) {
            $table->id();
            $table->string('job_id', 100)->unique();
            $table->text('facility')->nullable();
            $table->text('job_title')->nullable();
            $table->text('specialty')->nullable();
            $table->timestamp('last_updated')->useCurrent();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('hwl');
    }
};
