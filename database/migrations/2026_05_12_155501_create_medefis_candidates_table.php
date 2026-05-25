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
        Schema::create('medefis_candidates', function (Blueprint $table) {
            $table->id();
            $table->string('candidate_id')->unique();
            $table->text('candidate_name')->nullable();
            $table->text('email')->nullable();
            $table->text('profile_url')->nullable();
            $table->text('state')->nullable();
            $table->text('specialty')->nullable();
            $table->text('sub_specialty')->nullable();
            $table->timestamp('last_updated')->useCurrent();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('medefis_candidates');
    }
};
