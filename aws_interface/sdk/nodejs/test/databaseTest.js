// databaseTest.js

const Client = require('../aws_interface.js');
const assert = require("assert");

var client = new Client.Client();
const test_email = "ttest@gmail.com";
const test_password = "ttestpassword";
const test_partition = "test-partition";
const test_item = {"type" : "test"};
const read_groups = ['user'];
const write_groups = ['user'];
const new_field = "test_field";
const new_value = "test_value";
const new_item = {"type" : "test-mod2"};
var item_id;
const query = [{"option":"or","field":"type","condition":"eq","value":"test"}];

describe('Database Test', function() {
    //Set timeout of 10 seconds for async testing.
    this.timeout(10000);

    // Create an item on [test_partition] with [test_item], [read_groups], [write_groups]
    // Retrieve the item with [item_id] and check its id
    // Delete the item
    it('test databaseCreateItem, databaseGetItem, databaseDeleteItem', function(done){
        client.authLogin(test_email, test_password)
            .then(function(body) {
                client.databaseCreateItem(test_partition, test_item, read_groups, write_groups)
                    .then( async function (response) {
                        assert.ok(response['item_id']);
                        item_id = await response['item_id'];

                        client.databaseGetItem(item_id)
                            .then(async function(response) {
                                await response;
                                assert.equal(response['item']['id'], item_id);
                        });
                        client.databaseDeleteItem(item_id)
                            .then(function(response) {
                                assert.ok(response['success']);
                                done();
                        });
                    });
            });
    });

    // Get the number of items in [test_partition]
    it('test databaseGetItemCount', function(done){
        client.authLogin(test_email, test_password)
            .then(function(body) {
            client.databaseGetItemCount(test_partition,null, null)
                .then(function(response) {
                    assert.ok(response['item']['count']);
                    done();
            });
        });
    });

    // Get the list of items in [test_partition]
    it('test databaseGetItems', function(done){
        client.authLogin(test_email, test_password)
            .then(function(body) {
                client.databaseGetItems(test_partition,null, 10)
                    .then(function(response) {
                        assert.ok(response['items']);
                        done();
                });
        });
    });

    // Put new field and value([new_field], [new_value] to the item with [item_id]
    it('test databasePutItemField, databaseUpdateItem', function(done){
        client.authLogin(test_email, test_password)
            .then(function(body) {
                client.databaseCreateItem(test_partition, test_item, read_groups, write_groups)
                    .then(function (response) {
                        assert.ok(response['item_id']);
                        item_id = response['item_id'];

                        client.databasePutItemField(item_id, new_field, new_value)
                            .then(function(response) {
                                assert.ok(response['success']);
                            });

                        client.databaseUpdateItem(item_id, new_item, read_groups, write_groups)
                            .then(function(response) {
                                assert.ok(response['success']);
                                done();
                            });
                });
            });
    });

    //Get a list of items that satisfy [query] condition in [test_partition]
    it('test databaseQueryItems', function(done){
        client.authLogin(test_email, test_password)
            .then(function(body) {
                client.databaseQueryItems(test_partition, query, null, 10, false)
                    .then(function(response) {
                        assert.ok(response['items']);
                        done();
                });
            });
    });
});
