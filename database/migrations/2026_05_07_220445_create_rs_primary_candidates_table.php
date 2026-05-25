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
        Schema::create('rsprimary_candidates', function (Blueprint $table) {
            $table->id();
            $table->text('unique_id')->unique()->nullable();
            $table->text('name')->nullable();
            $table->text('first_name')->nullable();
            $table->text('last_name')->nullable();
            $table->text('email')->nullable();
            $table->text('phone')->nullable();
            $table->text('address')->nullable();
            $table->text('vendor')->nullable();
            $table->text('experience')->nullable();
            $table->text('bill_rate')->nullable();
            $table->text('ssn_last_4')->nullable();
            $table->text('skills')->nullable();
            $table->text('profile_url')->nullable();
            $table->timestamp('last_updated')->useCurrent()->useCurrentOnUpdate();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('rs_primary_candidates');
    }
};
