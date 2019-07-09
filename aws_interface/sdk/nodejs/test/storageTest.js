// databaseTest.js

const Client = require('../aws_interface.js');
const assert = require("assert");
const fs = require('fs');

var client = new Client.Client();
const test_email = "ttest@gmail.com";
const test_password = "ttestpassword";
const read_groups = ['user', 'admin'];
const write_groups = ['user', 'admin'];
const file_name = 'test.txt'
var file_id;
var file_b64;


describe('Storage Test', function() {

    //Create a textfile for testing.
    let data = "This is test file.";
    fs.writeFile('test.txt', data, (err) => {
        if (err) throw err;
    });

    // Upload a file with [file_name] with read permissions to [read_groups], write permissions to [write_groups]
    // Get [file_id] when uploading.
    // Download and delete the file with [file_id].
    // Wait for the upload and download to finish by async and await on response.
    it('test storageUploadFile,storageDownloadFile, storageDeleteFile', function(done) {
        client.authLogin(test_email, test_password, function (body) {
            client.storageUploadFile(file_name, read_groups, write_groups, async function (response) {
                file_id = await response['file_id'];
                assert.ok(response['file_id']);

                client.storageDownloadFile(file_id, async function (response) {
                    const rr = await response;
                    assert.ok(response);
                });

                client.storageDeleteFile(file_id, function (response) {
                    assert.ok(response['success']);
                });

            });
            done();
        });
    });
/*
    it('test storageDownloadB64Chunk, storageDeleteB64', function (done) {
        client.authLogin(test_email, test_password, function (body) {
            file_id = "N7PxzRdEK3nhE3GM53CAnb";

            client.storageDownloadB64Chunk(null, async function (response) {
                    file_b64 = await response['file_b64'];
                    console.log(response);
                    //assert.ok(response['file_64']);
                });
                client.storageDeleteB64(file_id, function (response) {
                    assert.ok(response['success']);
                    console.log(response);
                });

            done();
        });
    });
    it('test storageUploadB64Chunk', function (done) {
        client.authLogin(test_email, test_password, function (body) {

            client.storageDeleteB64(file_id, function (response) {
                assert.ok(response['success']);
            });
        });
        done();
    });
 */
});