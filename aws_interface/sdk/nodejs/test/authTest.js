// authTest.js

const Client = require('../aws_interface.js');
const assert = require("assert");

var client = new Client.Client();
const new_email = "test12@email.com";
const new_password = "test12password";
const test_email = "ttest@gmail.com";
const test_password = "ttestpassword";
const fb_token = "";
const user_id = "jK5iK6UgYnTdaRhow5yvAT";

describe('Auth Test', function() {

    //Register new user with [new_email], [new_password]
    //Function is commented since it gets already registered user when repeated.
    /*
    it('test authRegister', client.authRegister(new_email, new_password, {},function(body) {
        assert.equal(body['item']['email'] == test_email)
    }));
   */
    // Login and logout
    it('test login and logout', function(done){
        client.authLogin(test_email, test_password, function(body) {
            client.authLogout(function(response) {
                assert.ok(response['success']);
            });
        });
        done();
    });

/*
    //Login with facebook access token [fb_token]
    it('test authLoginFacebook', function(done){
        client.authLoginFacebook(fb_token, function(body){
            assert.ok(body['session_id']);

        });
        done();
    });

 */
    //Get user information with [user_id]
    it('test authGetUser', function(done){
        client.authLogin(test_email, test_password, function(body) {
            client.authGetUser(user_id, function(response) {
                assert.equal(response['item']['email'], test_email);
                assert.equal(response['item']['id'], user_id);
            });
        });
        done();
    });

    //Get a list of users
    it('test authGetUsers', function(done){
        client.authLogin(test_email, test_password, function(body) {
            client.authGetUsers(null, function(response) {
                assert.ok(response['items']);
            });
        });
        done();
    });

    //Guest login
    it('test authGuest', function(done){
        client.authLogin(test_email, test_password, function(body) {
            client.authGuest(null, function(response) {
                assert.ok(response['session_id']);
            });
        });
        done();
    });

});


