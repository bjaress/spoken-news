Feature: Reading the News

Background:
    Given the service is healthy
    Given Spreaker API is available

Scenario: Uploading sound
    When the scheduled time arrives
    Then an audio file is uploaded to Spreaker
