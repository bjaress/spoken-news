Feature: Reading the News

Background:
    Given the service is healthy
    Given there is an old refresh token stored

Scenario: Uploading sound
    When the scheduled time arrives
    Then the old refresh token is retrieved
    And the old refresh token is used to get an auth token and new refresh token
    And the new refresh token is saved
    And an audio file is uploaded to SoundCloud
