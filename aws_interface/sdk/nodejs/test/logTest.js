// logTest.js

const Client = require('../aws_interface.js');
const assert = require("assert");

var client = new Client.Client();
const test_email = "ttest@gmail.com";
const test_password = "ttestpassword";
const test_source = "test-source";
const test_event = "test-event-name";
const test_param = "test-param";


describe('Log Test', function() {

    //test create log with [test_source], [test_event], [test_param]
    //Currently forbidden request error
    /*
    it('test logCreateLog', function(done) {
        client.authLogin(test_email, test_password, function (body) {
            client.logCreateLog(test_source, test_event, test_param, function (response) {
                assert.ok(response['success']);
            });
            done();
        });
    });
     */
});