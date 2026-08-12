// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnerableBank {

    address public owner;
    mapping(address => uint256) public balances;

    constructor() {
        owner = msg.sender;
    }


    // ❌ Missing access control
    // Anyone can deposit on behalf of another address
    function deposit(address user) public payable {
        balances[user] += msg.value;
    }


    // ❌ REENTRANCY vulnerability
    // State update happens after external call
    function withdraw(uint256 amount) public {

        require(balances[msg.sender] >= amount);

        // External call before updating balance
        (bool success, ) = msg.sender.call{value: amount}("");

        require(success);

        balances[msg.sender] -= amount;
    }


    // ❌ tx.origin authentication vulnerability
    function adminWithdraw() public {

        require(tx.origin == owner);

        payable(owner).transfer(address(this).balance);
    }


    // ❌ Unchecked external call
    function sendEther(address payable receiver) public {

        receiver.call{value: 1 ether}("");

    }


    // ❌ Weak randomness
    function randomNumber() public view returns(uint256){

        return uint256(
            keccak256(
                abi.encodePacked(
                    block.timestamp,
                    block.prevrandao
                )
            )
        );

    }


    // ❌ Anyone can change owner
    function changeOwner(address newOwner) public {

        owner = newOwner;

    }


    // Helper function
    receive() external payable {}

}