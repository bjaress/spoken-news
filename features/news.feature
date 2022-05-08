Feature: Reading the News

Background:
    Given the service is healthy

Scenario: Simple Trigger
    When a message is posted
    Then the process runs
