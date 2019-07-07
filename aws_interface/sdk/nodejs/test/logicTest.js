// logTest.js

const Client = require('../aws_interface.js');
const assert = require("assert");

var client = new Client.Client();
const test_email = "ttest@gmail.com";
const test_password = "ttestpassword";
const test_function = "test-function"
const test_payload = {"answer" : 10};


describe('Logic Test', function() {

    // Run [test_function] with [test_payload]
    it('test logicRunFunction', function(done) {
        client.authLogin(test_email, test_password, function (body) {
            client.logicRunFunction(test_function, test_payload, function (response) {
            console.log(response);
        });
            done();
        });
    });
});