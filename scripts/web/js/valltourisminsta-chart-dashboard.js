// Inicializar el proveedor de credenciales de Amazon Cognito
AWS.config.region = 'eu-west-1'; // Región
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
	IdentityPoolId: "eu-west-1:bda8761f-9ad7-41b2-aa1d-8c09e00dfa22",
});

AWS.config.credentials.get(function(err) {
	if (err) {
		console.log("Error: " + err);
		return;
	}

	console.log("Cognito Identity Id: " + AWS.config.credentials.identityId);
	var cognitoSyncClient = new AWS.CognitoSync();
	cognitoSyncClient.listDatasets(
		{
			IdentityId: AWS.config.credentials.identityId,
			IdentityPoolId: "eu-west-1:bda8761f-9ad7-41b2-aa1d-8c09e00dfa22"
		},
		function(err, data) {
			if (err) {
				console.log("Error cognitoSyncClient: " + err, err.stack);
			}
			else {
				console.log("Success cognitoSyncClient: " + JSON.stringify(data));
			}
		}
	);
});

// you can now check that you can describe the DynamoDB table
var params = { TableName : "valltourisminsta" };
var dynamodb = new AWS.DynamoDB({ apiVersion: '2012-08-10' });
dynamodb.describeTable(params, function(err, data){
	if (err) {
		console.log("Error describeTable: " + err, err.stack);
	}
	else {
		console.log("Success describeTable: " + JSON.stringify(data));
	}
});

// query
function query() {
	var gender = document.querySelector('input[name="gender"]:checked').value;
	var ageLow = document.querySelector('input[name="ageLow"]').value;
	if ((gender == null) || (ageLow == null)) {
		console.log("Error query: missing input");
		return;
	}

	var params = {
		TableName : "valltourisminsta",
		Limit : 50,
		FilterExpression : "gender = :gender AND ageLow < :ageLow",
		ExpressionAttributeValues : {
			":gender" : { S : gender },
			":ageLow" : { N : ageLow }
		}
	};
	dynamodb.scan(params, function(err, data){
		if (err) {
			console.log("Error scan: " + err, err.stack);
		}
		else {
			console.log("Success scan: " + JSON.stringify(data));

			// Table
			table = document.getElementById("table");
			table.innerHTML = "<tr><th>id</th><th>faceIndex</th><th>timestamp</th><th>gender</th><th>ageLow</th></tr>";
			data.Items.forEach(function(item) {
				table.innerHTML += "<tr><td>" +
					item.id["S"] + '</td><td>' + item.faceIndex["N"] + '</td><td>' +
					item.timestamp["S"] + '</td><td>' + item.gender["S"] + '</td><td>' +
					item.ageLow["N"] + '</td></tr>';
			});

			// Plot
			labels = [ "happy", "surprised", "fear", "sad", "angry", "disgusted", "confused", "calm" ];
			labelCounts = {};
			labels.forEach(function(label) {
				labelCounts[label] = 0;
			})
			data.Items.forEach(function(item) {
				if (item.happyConfidence["N"] > 30.0) { labelCounts["happy"] += 1; }
				if (item.surprisedConfidence["N"] > 30.0) { labelCounts["surprised"] += 1; }
				if (item.fearConfidence["N"] > 30.0) { labelCounts["fear"] += 1; }
				if (item.sadConfidence["N"] > 30.0) { labelCounts["sad"] += 1; }
				if (item.angryConfidence["N"] > 30.0) { labelCounts["angry"] += 1; }
				if (item.disgustedConfidence["N"] > 30.0) { labelCounts["disgusted"] += 1; }
				if (item.confusedConfidence["N"] > 30.0) { labelCounts["confused"] += 1; }
				if (item.calmConfidence["N"] > 30.0) { labelCounts["calm"] += 1; }
			});

			var ctx = document.getElementById("canvas").getContext("2d");
			var chart = new Chart(ctx, {
				type : "bar",
				data : {
					labels : labels,
					datasets : [{
						label : 'Count emotion > 30',
						data : labelCounts,
						borderWidth : 1
					}]
				},
				options : {
					responsive : true,
					maintainAspectRatio: false
				}
			});
			chart.resize(300, 300);
		}
	});
}
