const request = require('request');
const base_url = '{{REST_API_URL}}';

class Client{

    constructor() {
        this.session_id = null;
    }

    static _get(object, key, default_value=null) {
        var result = object[key];
        return (typeof result !== "undefined") ? result : default_value;
    }

    _call_api(service_type, function_name, data, callback) {
        if (data == null){
            data = {};
        }
        data['module_name'] = 'cloud.' + service_type + '.' + function_name;
        if (this.session_id != null){
            data['session_id'] = this.session_id;
        }
        this._post(base_url, data, callback);
    }

    _post(url, data, callback){
        let options = {
            uri: base_url,
            method: 'POST',
            json: data,
        };
        request(options, function (error, response, body) {
            if (error) {
                callback({
                    'error': error,
                    'message': error.message,
                });
            }else{
                callback(body['body']);
            }
        });
    }

    _auth(api_name, data, callback) {
        let self = this;
        this._call_api('auth', api_name, data, function (data) {
            self.log_create_log('auth', api_name, null, function (data) {
                
            });
            callback(data);
        });
    }

    _database(api_name, data, callback) {
        let self = this;
        this._call_api('database', api_name, data, function (data) {
            self.log_create_log('database', api_name, null, function (data) {

            });
            callback(data);
        });
    }

    _storage(api_name, data, callback) {
        let self = this;
        this._call_api('storage', api_name, data, function (data) {
            self.log_create_log('storage', api_name, null, function (data) {

            });
            callback(data);
        });
    }

    _log(api_name, data, callback) {
        this._call_api('log', api_name, data, callback);
    }

    auth_register(email, password, extra={}, callback) {
        this._auth('register', {
            'email': email,
            'password': password,
            'extra': extra,
        }, callback);
    }

    auth_login(email, password, callback) {
        let self = this;
        this._auth('login', {
            'email': email,
            'password': password,
        }, function (data) {
            if ('session_id' in data){
                self.session_id = Client._get(data,'session_id');
            }
            callback(data);
        });
    }

    auth_get_user(user_id, callback) {
        this._auth('get_user', {
            'user_id': user_id,
        }, callback);
    }

    auth_get_users(start_key=null, callback) {
        this._auth('get_users', {
            'start_key': start_key,
        }, callback);
    }

    auth_logout(callback) {
        this._auth('logout', {
            'session_id': this.session_id,
        }, callback);
    }

    auth_guest(guest_id=null, callback) {
        let self = this;
        this._auth('guest', {
            'guest_id': guest_id,
        }, function (data) {
            self.session_id = Client._get(data,'session_id');
            callback(data);
        });
    }

    database_create_item(item, partition, read_groups, write_groups, callback) {
        this._database('create_item', {
            'item': item,
            'partition': partition,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }, callback);
    }

    database_delete_item(item_id, callback) {
        this._database('delete_item', {
            'item_id': item_id,
        }, callback);
    }

    database_get_item(item_id, callback) {
        this._database('get_item', {
            'item_id': item_id,
        }, callback);
    }

    database_get_items(partition, start_key=null, limit=100, callback) {
        this._database('get_items', {
            'partition': partition,
            'start_key': start_key,
            'limit': limit,
        }, callback);
    }

    database_put_item_field(item_id, field_name, field_value, callback) {
        this._database('put_item_field', {
            'item_id': item_id,
            'field_name': field_name,
            'field_value': field_value,
        }, callback);
    }

    database_update_item(item_id, item, read_groups, write_groups, callback) {
        this._database('update_item', {
            'item_id': item_id,
            'item': item,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }, callback);
    }

    database_query_items(partition, query, start_key=null, limit=100, reverse=false, callback) {
        this._database('query_items', {
            'partition': partition,
            'query': query,
            'start_key': start_key,
            'limit': limit,
            'reverse': reverse,
        }, callback);
    }

    storage_delete_b64(file_id, callback) {
        this._storage('delete_b64', {
            'file_id': file_id,
        }, callback);
    }

    storage_download_b64_chunk(file_id, callback) {
        this._storage('download_b64', {
            'file_id': file_id,
        }, callback);
    }

    storage_upload_b64_chunk(parent_file_id, file_name, file_b64, read_groups, write_groups, callback) {
        this._storage('upload_b64', {
            'parent_file_id': parent_file_id,
            'file_name': file_name,
            'file_b64': file_b64,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }, callback);
    }

    storage_delete_file(file_id, callback) {
        this.storage_delete_b64(file_id, callback);
    }

    storage_download_file(file_id, callback_file) {
        let self = this;
        var string_file_b64 = null;
        var file_name = 'file';
        function download(file_id, callback){
            self.storage_download_b64_chunk(file_id, function (result) {
                file_id = Client._get(result, 'parent_file_id', null);
                file_name = Client._get(result,'file_name', file_name);
                if (string_file_b64 != null){
                    string_file_b64 = Client._get(result, 'file_b64') + string_file_b64;
                }else{
                    string_file_b64 = Client._get(result, 'file_b64');
                }
                if (file_id == null){
                    callback(string_file_b64, result);
                }else{
                    download(file_id, callback);
                }
            });
        }
        download(file_id, function (string_file_b64, result) {
            if (string_file_b64 == null){
                callback_file(null);
                console.error(result);
            }else{
                let file_bin = Buffer.from(string_file_b64, 'base64');
                callback_file(file_bin);
            }
        });
    }

    storage_upload_file(bin, read_groups, write_groups, callback) {
        let self = this;
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
        let file_name = "file";
        function upload(parent_file_id, base64_chunk, callback){
            base64_chunk = base64_chunk.toString();
            self.storage_upload_b64_chunk(parent_file_id, file_name, base64_chunk, read_groups, write_groups, function (data) {
                var parent_file_id = data['file_id'];
                var next_base64_chunk = base64_chunks.next();
                if (next_base64_chunk.done){
                    callback(data);
                }else{
                    upload(parent_file_id, next_base64_chunk.value, callback);
                }
            });
        }
        upload(parent_file_id, base64_chunks.next().value, callback);
    }

    log_create_log(event_source, event_name, event_param, callback) {
        this._log('create_log', {
            'event_source': event_source,
            'event_name': event_name,
            'event_param': event_param,
        }, callback);
    }

}

module.exports.Client = Client;