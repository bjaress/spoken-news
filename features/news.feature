Feature: Reading the News

Background:
    Given the service is healthy
    Given Spreaker API is available
    Given Google text-to-speech API is available
    Given Wikipedia is available

Scenario: Single headline becomes episode
    Given there is a headline about frogs
    And there are articles about frogs
    When it is time to generate news
    Then news is retrieved from Wikipedia
    Then the list of past episodes is retrieved from Spreaker
    Then audio is generated about frogs
    Then the audio file is uploaded to Spreaker
    And the episode title is about frogs

# Rule: The oldest headline without an episode becomes an episode

Scenario: Two headlines, oldest has no episode
    Given there is a headline about frogs
    And there are articles about frogs
    And there is a headline about the nobel prize
    When it is time to generate news
    Then the list of past episodes is retrieved from Spreaker
    Then the audio file is uploaded to Spreaker
    And the episode title is about frogs

Scenario: Two headlines, oldest has an episode
    Given there is a headline about frogs
    And there is a headline about the nobel prize
    And there are articles about the nobel prize
    Given there is an episode about frogs
    When it is time to generate news
    Then the list of past episodes is retrieved from Spreaker
    Then the audio file is uploaded to Spreaker
    And the episode title is about the nobel prize

Scenario: Two headlines, both have episodes
    Given there is a headline about frogs
    And there is a headline about the nobel prize
    Given there is an episode about frogs
    And there is an episode about the nobel prize
    When it is time to generate news
    Then the list of past episodes is retrieved from Spreaker
    Then no audio file is uploaded to Spreaker

Scenario: Slightly altered headline
    Given there is a headline about frogs
    And there is an episode about toads
    When it is time to generate news
    Then the list of past episodes is retrieved from Spreaker
    Then no audio file is uploaded to Spreaker
