// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {CTF} from "../src/CTF.sol";

contract CTFTest is Test {
    CTF public ctf;

    address owner = address(0x1234);

    function setUp() public {
        vm.prank(owner);
        string memory password = "abc";
        ctf = new CTF(bytes32(keccak256(abi.encode(password))));
    }

    function test_Increment() public {
        // assertEq(ctf.number(), 1);
    }
}
