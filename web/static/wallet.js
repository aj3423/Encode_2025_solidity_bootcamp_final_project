function connect_wallet(callback) {
	if (typeof window.ethereum !== 'undefined') {

		window.ethereum
			.request({ method: 'eth_requestAccounts' })
			.then((accounts) => {
				const account = accounts[0]; // Get the first account
				console.log('Connected account:', account);

				callback()
			})
			.catch((error) => {
				alert('Error connecting:', error);
			});
	} else {
		alert('MetaMask is not installed.');
	}
}

// // sign
// const messageToSign = 'Hello, world!';
// signMessage(messageToSign).then((signature) => {
// 	if (signature) {
// 		console.log('Signature:', signature);
// 		// You can now send the message and signature to your backend for verification.
// 	}
// });

function connected_wallet(callback) {
	ethereum.request({ method: 'eth_accounts' }).then(callback).catch(console.error);

}
function is_wallet_connected(callback) {
	if (!window.ethereum) {
		callback(false)
	} else {
		connected_wallet(function(accounts) {
			callback(accounts.length > 0)
		})
	}
}

function sign_message(message, callback) {
	return window.ethereum
		.request({ method: 'eth_requestAccounts' })
		.then(accounts => {
			const account = accounts[0];
			return window.ethereum
				.request({
					method: 'personal_sign',
					params: [message, account],
				})
				.then(signature => {
					callback(account, signature)
				})
		})
}


