Feature: Reading the News

Background:
    Given the service is healthy
    Given Spreaker API is available
    Given Google text-to-speech API is available
    Given Wikipedia is available

Scenario: Uploading sound
    Given there is a headline about frogs
    When the scheduled time arrives
    Then news is retrieved from Wikipedia
    Then the list of past episodes is retrieved from Spreaker
    Then audio is generated about frogs
    Then the audio file is uploaded to Spreaker
    And the episode title is about frogs

# Rule: The oldest headline without an episode becomes an episode

Scenario: Two headlines, oldest has no episode
    Given there is a headline about frogs
    And there is a headline about the nobel prize
    When the scheduled time arrives
    Then the list of past episodes is retrieved from Spreaker
    Then the audio file is uploaded to Spreaker
    And the episode title is about frogs

Scenario: Two headlines, oldest has an episode
    Given there is a headline about frogs
    And there is a headline about the nobel prize
    Given there is an episode about frogs
    When the scheduled time arrives
    Then the list of past episodes is retrieved from Spreaker
    Then the audio file is uploaded to Spreaker
    And the episode title is about the nobel prize
