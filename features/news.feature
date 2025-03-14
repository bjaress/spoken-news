
Feature: speaking the news

  Background: Dependencies
    Given Spreaker is available
    Given Google is available
    Given Wikipedia is available
    Given the app is running

  Scenario: One simple news item
    Given there is a simple news item about frogs
    When it is time to generate news
    Then headlines are retrieved from Wikipedia
    And the episode list from Spreaker is retrieved
    And Wikipedia articles about frogs are retrieved
    And a script about frogs is sent for text-to-speech processing
    And an episode about frogs is uploaded to Spreaker

  Scenario: Linking to a section
    Given there is a news item about bananas that links to a section
    When it is time to generate news
    Then headlines are retrieved from Wikipedia
    And the episode list from Spreaker is retrieved
    And Wikipedia articles about bananas are retrieved
    And a script about bananas is sent for text-to-speech processing
    And an episode about bananas is uploaded to Spreaker

  Scenario: Long articles
    Given there is a news item with very long articles about sports
    When it is time to generate news
    Then headlines are retrieved from Wikipedia
    And the episode list from Spreaker is retrieved
    And Wikipedia articles about sports are retrieved
    And a script about sports is sent for text-to-speech processing
    And an episode about sports is uploaded to Spreaker

  # Choosing which story to use based on age, existing episodes

  Scenario: Two headlines, oldest has no episode
    Given there is a news item about bananas that links to a section
    Given there is a simple news item about frogs
    When it is time to generate news
    Then headlines are retrieved from Wikipedia
    And the episode list from Spreaker is retrieved
    And Wikipedia articles about frogs are retrieved
    And a script about frogs is sent for text-to-speech processing
    And an episode about frogs is uploaded to Spreaker

  Scenario: Two headlines, oldest has an episode
    Given there is a 10 day old episode about frogs
    Given there is a news item about bananas that links to a section
    Given there is a simple news item about frogs
    When it is time to generate news
    Then headlines are retrieved from Wikipedia
    And the episode list from Spreaker is retrieved
    And Wikipedia articles about bananas are retrieved
    And a script about bananas is sent for text-to-speech processing
    And an episode about bananas is uploaded to Spreaker

  Scenario: Two headlines, both with episodes
    Given there is a 10 day old episode about frogs
    Given there is a 5 day old episode about bananas
    Given there is a news item about bananas that links to a section
    Given there is a simple news item about frogs
    When it is time to generate news
    Then headlines are retrieved from Wikipedia
    And the episode list from Spreaker is retrieved
    And no scripts are sent for text-to-speech processing
    And no episodes are uploaded to Spreaker
