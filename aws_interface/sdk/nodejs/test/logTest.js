// logTest.js
const Client = require('../aws_interface.js');
const assert = require("assert");

var client = new Client.Client();
const test_email = "ttest@gmail.com";
const test_password = "ttestpassword";
const test_source = "test-source";
const test_event = "test-event-name";
const test_param = "test-param";
const log_owner = "user";

describe('Log Test', function() {
    //Set timeout of 7 seconds for async testing.
    this.timeout(7000);

    //test create log with [test_source], [test_event], [test_param]
    it('test logCreateLog', function(done){
        client.authLogin(test_email, test_password)
        .then(function(){
            client.logCreateLog(test_source, test_event, test_param)
                .then(function(response){
                    assert.ok(response['success']);
                    done(); // Signal that callback is done, so that finish the unit test.
                });
        });
    });

    //test get log with [test_source], [test_event], [test_param]
    it('test logGetLogs', function(done){
        client.authLogin(test_email, test_password)
            .then(function(){
                client.logGetLogs(test_source, test_event, log_owner, 0, false)
                    .then(function(response){
                        assert.ok(response['items']);
                        done(); // Signal that callback is done, so that finish the unit test.
                    });
            });
    });
});