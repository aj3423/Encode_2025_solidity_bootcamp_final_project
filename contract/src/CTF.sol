// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

contract CTF {
    address admin;

    // -------- competitors --------
    // aes encrypted addresses
    bytes20[] users;
    // aes encrypted address => name
    mapping(bytes20 => string) userNames;

    struct Solution {
        uint8 score;
        uint256 gasCost;
        bytes sourceCode; // aes encpypted source code
    }

    // This key is used to encrypt all addresses/source code.
    bytes16 encryptionKey;
    // user => level => Solution
    mapping(bytes20 => mapping(uint8 => Solution)) solutions;

    uint256 public deadline;

    modifier onlyAdmin() {
        require(msg.sender == admin, "only admin");
        _;
    }
    modifier isOnGoing() {
        require(deadline > 0, "not started yet");
        require(block.timestamp < deadline, "already ended");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    // ---- admin functions ----
    function register(
        bytes20 user,
        string memory name
    ) public onlyAdmin isOnGoing {
        require(bytes(name).length > 0, "empty name");

        // has not been set yet
        if (bytes(userNames[user]).length == 0) {
            users.push(user);
        }
        // else {
        // already set, only update the name
        // }
        userNames[user] = name;
    }

    function setDeadline(uint256 _deadline) public onlyAdmin {
        deadline = _deadline;
    }

    function setEncpyptionKey(bytes16 key) public onlyAdmin {
        encryptionKey = key;
    }

    function confirmSolution(
        bytes20 user,
        uint8 level,
        uint8 score,
        uint256 gasCost,
        bytes calldata sourceCode
    ) public isOnGoing onlyAdmin {
        Solution storage s = solutions[user][level];

        require(score >= s.score && gasCost >= s.gasCost, "even worse");

        solutions[user][level] = Solution(score, gasCost, sourceCode);
    }

    // ---- user functions ----
    function leaderboard(
        uint8[] calldata levels
    ) public view returns (string[] memory, Solution[] memory, bytes16) {
        uint usersLen = users.length;
        string[] memory names = new string[](usersLen);
        Solution[] memory _solutions = new Solution[](usersLen);

        for (uint i = 0; i < usersLen; i++) {
            bytes20 user = users[i];
            names[i] = userNames[user];

            for (uint j = 0; j < levels.length; j++) {
                uint8 lvl = levels[j];
                Solution memory s = solutions[user][lvl];
                _solutions[i].score += s.score;
                _solutions[i].gasCost += s.gasCost;
                _solutions[i].sourceCode = s.sourceCode;
            }
        }

        return (names, _solutions, encryptionKey);
    }
}
