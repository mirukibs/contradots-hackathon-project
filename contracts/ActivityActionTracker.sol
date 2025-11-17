// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;
import {ReputationTracker} from "./ReputationTracker.sol";

contract ActivityActionTracker {

    type ActivityId is uint256;
    type ActionId is uint256;
    type PersonId is uint256; // Used for leadId and personId

    // Map the ActionStatus enum
    enum ActionStatus { SUBMITTED, VALIDATED, REJECTED }

    // Map the Activity Aggregate Root
    struct Activity {
        ActivityId activityId;
        bytes32 name;        // string
        bytes32 description; // string
        PersonId leadId;     // PersonId
        uint256 points;      // int
        bool isActive;       // boolean
    }

    // Map the Action Aggregate Root
    struct Action {
        ActionId actionId;
        PersonId personId;     // PersonId
        ActivityId activityId; // ActivityId
        bytes32 description;   // string
        bytes32 proofHash;     // string (hash)
        ActionStatus status;   // ActionStatus
    }

    // --- State Variables ---

    // Storage for Activities and Actions, using incremental counters as IDs
    mapping(ActivityId => Activity) public activities;
    uint256 private nextActivityId = 1;

    mapping(ActionId => Action) public actions;
    uint256 private nextActionId = 1;

    address public reputationTrackerAddress;
    mapping(ActivityId => uint256) private activityPoints;

    // --- Events (Mapping PlantUML Domain Events) ---

    event ActivityCreated(
        ActivityId indexed activityId,
        PersonId indexed leadId,
        bytes32 name,
        uint256 points
    );

    event ActivityDeactivated(
        ActivityId indexed activityId
    );

    event ActionSubmittedEvent( // ActionSubmittedEvent
        ActionId indexed actionId,
        PersonId indexed personId,
        ActivityId indexed activityId,
        bytes32 description,
        bytes32 proofHash
    );

    event ProofValidatedEvent( // ProofValidatedEvent
        ActionId indexed actionId,
        PersonId indexed personId,
        ActivityId indexed activityId,
        bool isValid
    );


    // --- Activity Aggregate Logic ---

    /**
     * @dev Creates a new Activity. Only active activities can receive actions.
     * Maps to the Activity.create() function.
     * @param _name The name of the activity.
     * @param _description The description of the activity.
     * @param _leadId The ID of the person creating (leading) the activity.
     * @param _points The reputation points rewarded for completing the activity.
     */
    function createActivity(
        bytes32 _name,
        bytes32 _description,
        PersonId _leadId,
        uint256 _points
    ) public returns (ActivityId) {
        ActivityId newId = ActivityId.wrap(nextActivityId++);
        
        activities[newId] = Activity({
            activityId: newId,
            name: _name,
            description: _description,
            leadId: _leadId,
            points: _points,
            isActive: true
        });

        // Store points in the mapping so validateProof can access them
        activityPoints[newId] = _points;
        
        emit ActivityCreated(newId, _leadId, _name, _points);
        return newId;
    }

    /**
     * @dev Deactivates an existing Activity.
     * Maps to the Activity.deactivate() function.
     * @param _activityId The ID of the activity to deactivate.
     */
    function deactivateActivity(ActivityId _activityId) public {
        require(ActivityId.unwrap(activities[_activityId].activityId) != 0, "Activity not found.");
        require(activities[_activityId].isActive, "Activity is already inactive.");

        activities[_activityId].isActive = false;
        emit ActivityDeactivated(_activityId);
    }

    // --- Action Aggregate Logic ---

    /**
     * @dev Submits a new Action for an Activity.
     * Maps to the Action.submit() function and emits ActionSubmittedEvent.
     * @param _personId The ID of the person performing the action.
     * @param _activityId The ID of the activity the action is for.
     * @param _description A description of the action taken.
     * @param _proofHash A hash of the proof (e.g., a file or transaction hash).
     */
    function submitAction(
        PersonId _personId,
        ActivityId _activityId,
        bytes32 _description,
        bytes32 _proofHash
    ) public returns (ActionId) {
        require(activities[_activityId].isActive, "Activity is not active.");

        ActionId newId = ActionId.wrap(nextActionId++);

        actions[newId] = Action({
            actionId: newId,
            personId: _personId,
            activityId: _activityId,
            description: _description,
            proofHash: _proofHash,
            status: ActionStatus.SUBMITTED
        });

        emit ActionSubmittedEvent(newId, _personId, _activityId, _description, _proofHash);
        return newId;
    }

    /**
     * @dev Validates the proof for an Action, changing its status.
     * Maps to the Action.validateProof() function and emits ProofValidatedEvent.
     * @param _actionId The ID of the action to validate.
     * @param _isValid True to validate (set status to VALIDATED), False to reject (set status to REJECTED).
     */
    function validateProof(ActionId _actionId, bool _isValid) public {
        Action storage action = actions[_actionId];
        require(ActionId.unwrap(action.actionId) != 0, "Action not found.");
        require(action.status == ActionStatus.SUBMITTED, "Action is not pending validation.");
        
        ActionStatus newStatus = _isValid ? ActionStatus.VALIDATED : ActionStatus.REJECTED;
        action.status = newStatus;

        // Retrieve the reputation points associated with the activity
        uint256 points = activityPoints[action.activityId];
        
        // Calculate the score change based on validation result
        // Positive points for VALIDATED, negative points (reversal) for REJECTED.
        int256 scoreChange = _isValid ? int256(points) : int256(points) * -1;

        //Integrate with the ReputationTracker
        if (_isValid || action.status == ActionStatus.VALIDATED) {
             // In a robust system, this section would be more complex to handle
             // the reputation reservation/reversion flow noted in the PlantUML.
             // For this MVP, we directly update based on the final status.
             
             // Cast the address and call the external contract function (convert PersonId between contracts)
             ReputationTracker(reputationTrackerAddress).updateReputation(
                 ReputationTracker.PersonId.wrap(PersonId.unwrap(action.personId)),
                 scoreChange
             );
        }

        action.status = newStatus;
        emit ProofValidatedEvent(action.actionId, action.personId, action.activityId, _isValid);

        // In a complete system, this event would trigger the reputation service update/revert
        emit ProofValidatedEvent(action.actionId, action.personId, action.activityId, _isValid);
    }

    function setReputationTrackerAddress(address _reputationTrackerAddress) public {
        // Simple access control: only the deployer/owner can set this (needs proper ownership in production)
        require(reputationTrackerAddress == address(0), "Tracker address already set.");
        reputationTrackerAddress = _reputationTrackerAddress;
    }
}

