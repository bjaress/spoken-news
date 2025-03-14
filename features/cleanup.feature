
Feature: Cleaning Up Old Data

  Background: Dependencies
    Given Spreaker is available
    Given the app is running

  Scenario: Removing an old episode
      Given there is a 10 day old episode about frogs
      Given there is a 3 day old episode about toads
      When it is time to clean up episodes older than 5 days
      Then the episode list from Spreaker is retrieved
      And the episode about frogs is deleted
      And the episode about toads is kept
