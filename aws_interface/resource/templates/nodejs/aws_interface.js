var request = require('request');
const base_url = '{{REST_API_URL}}';

let client = function() {
    var session_id = null;

    function get(object, key, default_value=null) {
        var result = object[key];
        return (typeof result !== "undefined") ? result : default_value;
    }

    function call_api(service_type, function_name, data, callback) {
        var data = data;
        if (data == null){
            data = {};
        }
        data['module_name'] = 'cloud.' + service_type + '.' + function_name;
        if (session_id != null){
            data['session_id'] = session_id;
        }
        post(base_url, data, callback);
    }

    function post(url, data, callback){
        let options = {
            uri: base_url,
            method: 'POST',
            json: data,
        };
        request(options, function (error, response, body) {
            if (error) {
                console.log(error);
                callback({
                    'error': error,
                    'message': error.message,
                });
            }else{
                callback(body['body']);
            }
        });
    }

    function auth(api_name, data, callback) {
        call_api('auth', api_name, data, callback);
    }

    function database(api_name, data, callback) {
        call_api('database', api_name, data, callback);
    }

    function storage(api_name, data, callback) {
        call_api('storage', api_name, data, callback);
    }

    function log(api_name, data, callback) {
        call_api('log', api_name, data, callback);
    }

    function auth_register(email, password, extra={}, callback) {
        auth('register', {
            'email': email,
            'password': password,
            'extra': extra,
        }, callback);
    }

    function auth_login(email, password, callback) {
        auth('login', {
            'email': email,
            'password': password,
        }, function (data) {
            session_id = get(data,'session_id');
            callback(data);
        });
    }

    function auth_get_user(user_id, callback) {
        auth('get_user', {
            'user_id': user_id,
        }, callback);
    }

    function auth_get_users(start_key=null, callback) {
        auth('get_users', {
            'start_key': start_key,
        }, callback);
    }

    function auth_logout(callback) {
        auth('logout', {
            'session_id': session_id,
        }, callback);
    }

    function auth_guest(guest_id=null, callback) {
        auth('guest', {
            'guest_id': guest_id,
        }, function (data) {
            session_id = get(data,'session_id');
            callback(data);
        });
    }

    function database_create_item(item, partition, read_groups, write_groups, callback) {
        database('create_item', {
            'item': item,
            'partition': partition,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }, callback);
    }

    function database_delete_item(item_id, callback) {
        database('delete_item', {
            'item_id': item_id,
        }, callback);
    }

    function database_get_item(item_id, callback) {
        database('get_item', {
            'item_id': item_id,
        }, callback);
    }

    function database_get_items(partition, start_key=null, limit=100, callback) {
        database('get_items', {
            'partition': partition,
            'start_key': start_key,
            'limit': limit,
        }, callback);
    }

    function database_put_item_field(item_id, field_name, field_value, callback) {
        database('put_item_field', {
            'item_id': item_id,
            'field_name': field_name,
            'field_value': field_value,
        }, callback);
    }

    function database_update_item(item_id, item, read_groups, write_groups, callback) {
        database('update_item', {
            'item_id': item_id,
            'item': item,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }, callback);
    }

    function database_query_items(partition, query, start_key=null, limit=100, reverse=false, callback) {
        database('query_items', {
            'partition': partition,
            'query': query,
            'start_key': start_key,
            'limit': limit,
            'reverse': reverse,
        }, callback);
    }

    function storage_delete_b64(file_id, callback) {
        database('delete_b64', {
            'file_id': file_id,
        }, callback);
    }

    function storage_download_b64_chunk(file_id, callback) {
        database('download_b64', {
            'file_id': file_id,
        }, callback);
    }

    function storage_upload_b64_chunk(parent_file_id, file_name, file_b64, read_groups, write_groups, callback) {
        database('upload_b64', {
            'parent_file_id': parent_file_id,
            'file_name': file_name,
            'file_b64': file_b64,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }, callback);
    }
    
    function storage_delete_file(file_id, callback) {
        storage_delete_b64(file_id, callback);
    }
    
    function storage_download_file(file_id, callback_bin) {
        var file_id = file_id;
        var string_file_b64 = null;
        var file_name = 'file';
        function download(file_id, callback){
            storage_download_b64_chunk(file_id, function (result) {
                file_id = get(result, 'parent_file_id', null);
                file_name = get(result,'file_name', file_name);
                if (string_file_b64 != null){
                    string_file_b64 = result['file_b64'] + string_file_b64;
                }else{
                    string_file_b64 = result['file_b64'];
                }
                if (file_id == null){
                    callback(string_file_b64);
                }else{
                    download(file_id, callback);
                }
            });
        }
        download(file_id, function (string_file_b64) {
            var string_b64 = Buffer.from(string_file_b64, 'utf8');
            var file_bin = Buffer.from(string_b64, 'base64');
            callback_bin(file_bin);
        });
    }

    function storage_upload_file(bin, read_groups, write_groups, callback) {
        function *div_chunks(text, n){
            for (var i = 0; i < text.length; i+= n){
                yield text.slice(i, i + n);
            }
        }
        var buff = Buffer.from(bin, 'utf8');
        let base64_data = buff.toString('base64');
        var raw_base64 = Buffer.from(base64_data, 'utf8');
        var base64_chunks = div_chunks(raw_base64, 1024 * 1024 * 6);
        var parent_file_id = null;
        function upload(parent_file_id, base64_chunk, callback){
            storage_upload_b64_chunk(parent_file_id, file_name, base64_chunk, read_groups, write_groups, function (data) {
                var parent_file_id = data['file_id'];
                var next_base64_chunk = base64_chunks.next();
                if (next_base64_chunk.done){
                    callback(data);
                }else{
                    upload(parent_file_id, next_base64_chunk.value, callback);
                }
            });
        }
        upload(parent_file_id, base64_chunk.next().value, callback);
    }
    
    function log_create_log(event_source, event_name, event_param, callback) {
        log('create_log', {
            'event_source': event_source,
            'event_name': event_name,
            'event_param': event_param,
        }, callback);
    }

    return{
        auth: {
            register: auth_register,
            login: auth_login,
            get_user: auth_get_user,
            get_users: auth_get_users,
            logout: auth_logout,
            guest: auth_guest,
        },
        database: {
            create_item: database_create_item,
            delete_item: database_delete_item,
            get_item: database_get_item,
            get_items: database_get_items,
            put_item_field: database_put_item_field,
            query_items: database_query_items,
            update_item: database_update_item,
        },
        storage: {
            delete_file: storage_delete_file,
            download_file: storage_download_file,
            upload_file: storage_upload_file,
        },
        log: {
            create_log: log_create_log,
        }
    }
}();
module.exports = exports = client;