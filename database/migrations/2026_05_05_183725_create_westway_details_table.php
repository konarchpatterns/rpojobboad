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
        Schema::create('westway_details', function (Blueprint $table) {
            $table->id();
            $table->string('job_id', 50)->unique();
            $table->text('position')->nullable();
            $table->text('status')->nullable();
            $table->string('pay_range')->nullable();
            $table->string('opened')->nullable();
            $table->text('dates')->nullable();
            $table->text('shift_info')->nullable();
            $table->text('description')->nullable();
            $table->text('company_name')->nullable();
            $table->timestamp('last_updated')->useCurrent();
            $table->timestamps();

            $table->foreign('job_id')->references('job_id')->on('westway')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('westway_details');
    }
};
