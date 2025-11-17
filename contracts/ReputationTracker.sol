// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

/**
 * @title ReputationTracker
 * @dev Manages person reputation scores based on validated actions.
 * Listens to events from the ActivityActionTracker contract.
 */
contract ReputationTracker {
    // Simplified PersonId as uint256
    type PersonId is uint256;
    type ActivityId is uint256;

    // Maps PersonId to their current reputation score (ReputationScore : int)
    mapping(PersonId => int256) public reputationScores;

    // The address of the trusted ActivityActionTracker contract
    address public activityActionTrackerAddress;

    // Define the events we are interested in from the other contract
    event ActionSubmittedEvent(
        uint256 indexed actionId,
        uint256 indexed personId,
        uint256 indexed activityId,
        bytes32 description,
        bytes32 proofHash
    );

    event ProofValidatedEvent(
        uint256 indexed actionId,
        uint256 indexed personId,
        uint256 indexed activityId,
        bool isValid
    );

    // Reputation update event
    event ReputationUpdated(
        PersonId indexed personId,
        int256 scoreChange,
        int256 newTotalScore
    );

    /**
     * @dev Constructor sets the address of the trusted ActivityActionTracker.
     * @param _activityActionTracker The address of the deployed tracker contract.
     */
    constructor(address _activityActionTracker) {
        activityActionTrackerAddress = _activityActionTracker;
    }

    // --- External Reputation Update Logic ---

    /**
     * @dev The core logic for updating reputation. This function MUST ONLY be called
     * by the trusted ActivityActionTracker.
     * Maps to ReputationService.updatePersonReputation().
     * @param _personId The ID of the person whose score is being updated.
     * @param _points The change in reputation score (can be positive or negative).
     */
    function updateReputation(PersonId _personId, int256 _points) public {
        require(msg.sender == activityActionTrackerAddress, "Only the ActivityActionTracker can update reputation.");

        reputationScores[_personId] += _points;

        emit ReputationUpdated(_personId, _points, reputationScores[_personId]);
    }
}