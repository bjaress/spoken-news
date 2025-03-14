Feature: Cleaning up old episodes

Background:
    Given the service is healthy
    Given Spreaker API is available

Scenario: Removing an old episode
    Given there is a 10 day old episode about frogs
    Given there is a 3 day old episode about toads
    When it is time to clean up episodes older than 5 days
    Then the list of past episodes is retrieved from Spreaker
    And the episode about frogs is deleted
    And the episode about toads is kept
