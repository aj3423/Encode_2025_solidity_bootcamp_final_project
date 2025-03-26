// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

interface ILv0 {
    function solution() external pure returns (uint8);
}

contract Lv0 {
    function verify(
        address studentContract
    ) external payable returns (uint8 score, uint256 gasCost) {
        uint256 gas1 = gasleft();
        uint8 ret = ILv0(studentContract).solution();
        uint256 gas2 = gasleft();
        require(ret == 42, "not 42");
        score = 2;
        gasCost = gas1 - gas2;
    }
}
