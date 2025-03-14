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
    And the episode description complies with Wikipedia's license
    And the episode description links to articles on frogs

Scenario: Linking to section
    Given there is a headline about banana peels
    And there are articles about bananas
    When it is time to generate news
    Then news is retrieved from Wikipedia
    Then audio is generated about banana peels
    Then the audio file is uploaded to Spreaker
    And the episode description links to articles on bananas

Scenario: Handling some templates
    Given there is a headline about outer space
    And there are articles about outer space
    When it is time to generate news
    Then news is retrieved from Wikipedia
    Then audio is generated about outer space


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
    Then audio is generated about the nobel prize
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

# Rule: Truncate long episodes to satisfy Google TTS

Scenario: Long episode
    Given there is a headline about sports
    And there are articles about sports
    When it is time to generate news
    Then audio is generated about sports
    Then the audio file is uploaded to Spreaker
