// authTest.js

const Client = require('../aws_interface.js');
const assert = require("assert");

var client = new Client.Client();
const new_email = "test21@email.com";
const new_password = "test21password";
const test_email = "ttest@gmail.com";
const test_password = "ttestpassword";
const fb_token = "";
const user_id = "jK5iK6UgYnTdaRhow5yvAT";

describe('Auth Test', function() {
    //Set timeout of 7 seconds for async testing.
    this.timeout(7000);

    //Register new user with [new_email], [new_password]
    //Function is commented since it gets already registered user when repeated.
    /*
    it('test authRegister', function(){
         client.authRegister(new_email, new_password, {})
             .then(function(body) {
                 assert.equal(body['item']['email'] == test_email);
             });
     });
    */

    // Login and logout
    it('test login and logout', function(done){
        client.authLogin(test_email, test_password)
            .then(function(){
                client.authLogout().then(function(response) {
                        assert.ok(response['success']);
                        done();
                    });
            });
    });


    //Login with facebook access token [fb_token]
    it('test authLoginFacebook', function(done){
        client.authLoginFacebook(fb_token)
            .then(function(body){
                assert.ok(body['session_id']);
                done();
            });
        });
    });


    //Get user information with [user_id]
    it('test authGetUser', function(done){
        //Extend timeout to 10 seconds
        this.timeout(10000);
        client.authLogin(test_email, test_password)
            .then(function(body) {
                client.authGetUser(user_id)
                    .then(function(response){
                        assert.equal(response['item']['email'], test_email);
                        assert.equal(response['item']['id'], user_id);
                        done();
                    });
            });
    });

    //Get a list of users
    it('test authGetUsers', function(done){
        client.authLogin(test_email, test_password)
            .then(function(body) {
                client.authGetUsers(null,)
                    .then(function(response) {
                        assert.ok(response['items']);
                        done();
                    });
            });
    });

    //Guest login
    it('test authGuest', function(done){
            client.authGuest(null)
                .then(function(response) {
                    assert.ok(response['session_id']);
                    done();
                });
    });