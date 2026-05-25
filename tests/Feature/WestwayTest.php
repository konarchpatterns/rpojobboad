<?php

use App\Models\User;

it('shows the westway job listings page', function () {
    $user = User::factory()->create();

    $response = $this
        ->actingAs($user)
        ->get('/westway');

    $response->assertStatus(200);
    $response->assertInertia(fn ($page) => $page
        ->component('Westway/Index')
        ->has('jobs')
    );
});
