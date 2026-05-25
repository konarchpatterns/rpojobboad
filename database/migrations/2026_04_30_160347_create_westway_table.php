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
        Schema::create('westway', function (Blueprint $table) {
            $table->id();
            $table->string('job_id', 50)->unique();
            $table->string('company_id', 50)->nullable();
            $table->text('company_name')->nullable();
            $table->text('status')->nullable();
            $table->string('opened')->nullable();
            $table->string('start_date')->nullable();
            $table->string('end_date')->nullable();
            $table->text('position')->nullable();
            $table->text('department')->nullable();
            $table->integer('qty')->nullable();
            $table->text('job_type')->nullable();
            $table->timestamp('last_updated')->useCurrent();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('westway');
    }
};
