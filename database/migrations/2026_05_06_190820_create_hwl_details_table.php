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
        Schema::create('hwl_details', function (Blueprint $table) {
            $table->id();
            $table->string('job_id', 100)->unique();
            $table->text('address')->nullable();
            $table->text('shift')->nullable();
            $table->text('weeks')->nullable();
            $table->jsonb('pay_rates')->nullable();
            $table->timestamp('last_updated')->useCurrent();
            $table->timestamps();

            $table->foreign('job_id')->references('job_id')->on('hwl')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('hwl_details');
    }
};
