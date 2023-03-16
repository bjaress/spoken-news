Feature: Reading the News

Background:
    Given the service is healthy
    Given Spreaker API is available
    Given Google text-to-speech API is available
    Given Wikipedia is available

Scenario: Uploading sound
    When the scheduled time arrives
    Then news is retrieved from Wikipedia
    Then audio is generated from text
    Then the audio file is uploaded to Spreaker
    And the episode title is based on the headline


