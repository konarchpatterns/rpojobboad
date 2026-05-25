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
        Schema::create('westway_candidates', function (Blueprint $table) {
            $table->id();
            $table->string('appl_id', 50)->unique();
            $table->string('company_id', 100)->nullable();
            $table->string('company_name', 255)->nullable();
            $table->string('status', 10)->nullable();
            $table->string('first_name', 100)->nullable();
            $table->string('last_name', 100)->nullable();
            $table->string('mi', 10)->nullable();
            $table->string('ssn', 50)->nullable();
            $table->string('city', 100)->nullable();
            $table->string('email', 255)->nullable();
            $table->string('home_phone', 50)->nullable();
            $table->string('cell_phone', 50)->nullable();
            $table->date('date_available')->nullable();
            $table->timestamp('last_updated')->useCurrent()->useCurrentOnUpdate();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('westway_candidates');
    }
};
