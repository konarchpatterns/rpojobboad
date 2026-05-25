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
        Schema::create('trovms_candidates', function (Blueprint $table) {
            $table->id();
            $table->string('candidate_number', 50)->unique()->nullable();
            $table->string('candidate_uuid', 100)->nullable();
            $table->string('name', 255)->nullable();
            $table->string('npi', 100)->nullable();
            $table->string('phone', 100)->nullable();
            $table->string('email', 255)->nullable();
            $table->string('years_exp', 50)->nullable();
            $table->string('travel_exp', 50)->nullable();
            $table->text('selling_points')->nullable();
            $table->timestamp('last_updated')->useCurrent()->useCurrentOnUpdate();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('trovms_candidates');
    }
};
