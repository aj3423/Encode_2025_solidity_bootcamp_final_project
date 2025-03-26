// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

interface ILv1 {
    function solution(
        uint256[2][3] calldata x,
        uint256[2][3] calldata y
    ) external pure returns (uint256[2][3] memory);
}

contract Lv1 {
    function verify(
        address studentContract
    ) external payable returns (uint8 score, uint256 gasCost) {
        uint256 gas1 = gasleft();
        uint256[2][3] memory x = [
            [uint256(1), uint256(2)],
            [uint256(3), uint256(4)],
            [uint256(5), uint256(6)]
        ];
        uint256[2][3] memory y = [
            [uint256(1), uint256(2)],
            [uint256(3), uint256(4)],
            [uint256(5), uint256(6)]
        ];
        uint256[2][3] memory z = [
            [uint256(2), uint256(4)],
            [uint256(6), uint256(8)],
            [uint256(10), uint256(12)]
        ];
        uint256[2][3] memory ret = ILv1(studentContract).solution(x, y);
        uint256 gas2 = gasleft();
        require(compareArrays(z, ret), "not match");
        score = 3;
        gasCost = gas1 - gas2;
    }

    function compareArrays(
        uint256[2][3] memory a,
        uint256[2][3] memory b
    ) internal pure returns (bool) {
        for (uint256 i = 0; i < 3; i++) {
            for (uint256 j = 0; j < 2; j++) {
                if (a[i][j] != b[i][j]) {
                    return false;
                }
            }
        }
        return true;
    }
}
