import { ethers } from "https://cdnjs.cloudflare.com/ajax/libs/ethers/6.7.0/ethers.min.js";

$(document).ready(function() {
	let connect = $('#connect_wallet')
	let leaderboard_section = $('#leaderboard_section')
	let form = $('form')
	let submit = $('#submit')

	function check_connected() {
		is_wallet_connected(function(connected) {
			if (connected) {
				form.show()
				submit.show()
				connect.hide()
				leaderboard_section.show()
				refresh_leaderboard()
			} else {
				form.hide()
				submit.hide()
				connect.show()
				leaderboard_section.hide()
			}
		})
	}
	check_connected()

	connect.on('click', function() {
		connect_wallet(check_connected)
	})

})

async function refresh_leaderboard() {
	const providerUrl = "https://eth-sepolia.public.blastapi.io/"; //
	const contractAddress = window.ctfContract;
	const contractABI = [
		{
			"name": "leaderboard",
			"type": "function",
			"stateMutability": "view", // or "nonpayable" depending on your contract
			"inputs": [
				{
					"name": "levels",
					"type": "uint8[]"
				}
			],
			"outputs": [
				{
					"name": "names",
					"type": "string[]"
				},
				{
					"name": "solutions",
					"type": "tuple[]",
					"components": [
						{
							"name": "score",
							"type": "uint8"
						},
						{
							"name": "gasCost",
							"type": "uint256"
						},
						{
							"name": "sourceCode",
							"type": "bytes"
						}
					]
				},
				{
					"name": "encKey",
					"type": "bytes16"
				},
			]
		}
	];

	// Create a provider.
	const provider = new ethers.JsonRpcProvider(providerUrl);

	// Create contract instance.
	const contract = new ethers.Contract(contractAddress, contractABI, provider);

	const levels = currPage.startsWith('Lv') ? [Number(currPage.substring(2))] : Array.from({ length: levelCount }, (_, i) => i);


	// Call the contract function
	const result = await contract.leaderboard(levels);
	const [names, raw_solutions, aesKey] = result;

	// Format solutions (ethers returns BigNumber for numeric values)
	const solutions = raw_solutions.map((solution, i) => ({
		name: names[i],
		score: Number(solution.score),
		gasCost: Number(solution.gasCost),
		sourceCode: solution.sourceCode // hex string
	}));

	solutions.sort((a, b) => {
		if (a.score !== b.score) {
			return b.score - a.score;
		}
		return a.gasCost - b.gasCost;
	});

	var columnCount = $("#leaderboard thead tr th").length;

	for (let i = 0; i < solutions.length; i++) {
		let sol = solutions[i]

		let $tr = $('<tr>');

		let $tdName = $('<td>').text(sol.name);
		let $tdScore = $('<td>').text(sol.score);
		let $tdGasCost = $('<td>').text(sol.gasCost);
		let $button = $('<button>').text('view').click(function() {

			if (aesKey && aesKey.length == 34) {
				let key = hex2bytes(aesKey.substring(2));
				const ciphertextBytes = hex2bytes(sol.sourceCode.substring(2));
				const nonce = new TextEncoder().encode("00000000");

				(async function() {
					try {
						const plaintextBytes = await aesCtrDecrypt(ciphertextBytes.buffer, key, nonce);
						const plaintext = new TextDecoder().decode(plaintextBytes);
						alert("Source code: \n\n" + plaintext);
					} catch (error) {
						alert("Decryption failed: " + error.message);
					}
				})();


			} else {
				alert('not over yet');
			}
		});
		let $tdSolution = $('<td>').append($button);

		$tr.append($tdName).append($tdScore).append($tdGasCost)
		if (columnCount == 4) {
			$tr.append($tdSolution)
		}

		$("#leaderboard tbody").append($tr);
	}
}


function hex2bytes(hex) {
	return new Uint8Array(hex.match(/.{1,2}/g).map(byte => parseInt(byte, 16))); // remove the '0x'
}
async function aesCtrDecrypt(ciphertext, keyBytes, nonce) {
	// Prepare the 16-byte counter block.
	// Place the 8-byte nonce into the beginning of the counter.
	let counter = new Uint8Array(16);
	counter.set(nonce, 0);
	// The remaining 8 bytes (the block counter) will be left as 0 initially.

	// Import the key to a CryptoKey object.
	const cryptoKey = await crypto.subtle.importKey(
		"raw",
		keyBytes,
		{ name: "AES-CTR" },
		false,
		["decrypt"]
	);

	// Setup AES-CTR parameters. Here, the counter length is 64 bits.
	const algorithm = {
		name: "AES-CTR",
		counter: counter,
		length: 64 // 64 bits of counter (the remaining 8 bytes)
	};

	// Perform the decryption. Note: ciphertext should be an ArrayBuffer.
	const plaintextBuffer = await crypto.subtle.decrypt(
		algorithm,
		cryptoKey,
		ciphertext
	);

	return new Uint8Array(plaintextBuffer);
}


