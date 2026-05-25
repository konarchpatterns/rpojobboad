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
        Schema::table('trovms', function (Blueprint $table) {
            $table->text('description')->nullable()->after('job_type');
            $table->json('details_json')->nullable()->after('description');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('trovms', function (Blueprint $table) {
            $table->dropColumn(['description', 'details_json']);
        });
    }
};
