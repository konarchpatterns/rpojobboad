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
        Schema::create('vms_candidates', function (Blueprint $table) {
            $table->id();
            $table->text('name')->nullable();
            $table->string('email', 255);
            $table->text('phone')->nullable();
            $table->text('state')->nullable();
            $table->text('status')->nullable();
            $table->text('profession')->nullable();
            $table->text('specialty')->nullable();
            $table->timestamp('last_updated')->useCurrent()->useCurrentOnUpdate();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('vms_candidates');
    }
};
