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
        Schema::create('favorite_staffing', function (Blueprint $table) {
            $table->id();
            $table->string('order_id', 50)->unique();
            $table->text('order_type')->nullable();
            $table->text('status')->nullable();
            $table->text('location')->nullable();
            $table->text('start_date')->nullable();
            $table->text('end_date')->nullable();
            $table->text('shift')->nullable();
            $table->text('hours')->nullable();
            $table->text('job_class')->nullable();
            $table->text('area')->nullable();
            $table->timestamp('last_seen')->useCurrent();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('favorite_staffing');
    }
};
