class Client{

    constructor() {
        this.set_session_id(null);
        this.setBaseUrl('{{REST_API_URL}}');
    }

    getBaseUrl(){
        return this.baseUrl;
    }

    setBaseUrl(baseUrl){
        this.baseUrl = baseUrl;
    }

    get_session_id(){
        return this.session_id;
    }

    set_session_id(session_id){
        this.session_id = session_id;
    }

    static _get(object, key, defaultValue=null) {
        var result = object[key];
        return (typeof result !== "undefined") ? result : defaultValue;
    }

    callAPI(service_name, api_name, data, callback) {
        if (data == null){
            data = {};
        }
        data['module_name'] = 'cloud.' + service_name + '.' + api_name;
        if (this.get_session_id() != null){
            data['session_id'] = this.get_session_id();
        }
        this._post(this.getBaseUrl(), data, callback);
    }

    _post(url, data, callback){
        var req = new XMLHttpRequest();
        req.open("POST", url, true);
        req.setRequestHeader("Accept", "application/json");
        req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        req.onreadystatechange = function (aEvt) {
          if (req.readyState == 4) {
            var json = JSON.parse(req.responseText);
            var body = null;
            var error = null;
            if ("body" in json){
              body = json["body"];
            }
            if ("error" in json){
              error = json["error"];
              console.error(error);
            }
            callback(body);
          }
        };
        req.send(JSON.stringify(data));
    }

    _auth(api_name, data, callback) {
        this.callAPI('auth', api_name, data, callback);
    }

    _database(api_name, data, callback) {
        this.callAPI('database', api_name, data, callback);
    }

    _storage(api_name, data, callback) {
        this.callAPI('storage', api_name, data, callback);
    }

    _logic(api_name, data, callback) {
        this.callAPI('logic', api_name, data, callback);
    }

    _log(api_name, data, callback) {
        this.callAPI('log', api_name, data, callback);
    }

    authRegister(email, password, extra={}, callback) {
        this._auth('register', {
            'email': email,
            'password': password,
            'extra': extra,
        }, callback);
    }

    authLogin(email, password, callback) {
        let self = this;
        this._auth('login', {
            'email': email,
            'password': password,
        }, function (data) {
            if ('session_id' in data){
                self.set_session_id(Client._get(data,'session_id'));
            }
            callback(data);
        });
    }

    authLoginFacebook(access_token, callback) {
        let self = this;
        this._auth('login_facebook', {
            'access_token': access_token,
        }, function (data) {
            if ('session_id' in data){
                self.set_session_id(Client._get(data,'session_id'));
            }
            callback(data);
        });
    }

    authGetUser(user_id, callback) {
        this._auth('get_user', {
            'user_id': user_id,
        }, callback);
    }

    authGetUsers(start_key=null, callback) {
        this._auth('get_users', {
            'start_key': start_key,
        }, callback);
    }

    authLogout(callback) {
        this._auth('logout', {
            'session_id': this.get_session_id(),
        }, callback);
    }

    authGuest(guest_id=null, callback) {
        let self = this;
        this._auth('guest', {
            'guest_id': guest_id,
        }, function (data) {
            self.set_session_id(Client._get(data,'session_id'));
            callback(data);
        });
    }

    databaseCreateItem(partition, item, read_groups, write_groups, callback) {
        this._database('create_item', {
            'item': item,
            'partition': partition,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }, callback);
    }

    databaseDeleteItem(item_id, callback) {
        this._database('delete_item', {
            'item_id': item_id,
        }, callback);
    }

    databaseGetItem(item_id, callback) {
        this._database('get_item', {
            'item_id': item_id,
        }, callback);
    }

    databaseGetItemCount(partition, field=null, value=null, callback) {
        this._database('get_item_count', {
            'item_id': item_id,
            'field': field,
            'value': value,
        }, callback);
    }

    databaseGetItems(partition, start_key=null, limit=100, callback) {
        this._database('get_items', {
            'partition': partition,
            'start_key': start_key,
            'limit': limit,
        }, callback);
    }

    databasePutItemField(item_id, field_name, field_value, callback) {
        this._database('put_item_field', {
            'item_id': item_id,
            'field_name': field_name,
            'field_value': field_value,
        }, callback);
    }

    databaseUpdateItem(item_id, item, read_groups, write_groups, callback) {
        this._database('update_item', {
            'item_id': item_id,
            'item': item,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }, callback);
    }

    databaseQueryItems(partition, query, start_key=null, limit=100, reverse=false, callback) {
        this._database('query_items', {
            'partition': partition,
            'query': query,
            'start_key': start_key,
            'limit': limit,
            'reverse': reverse,
        }, callback);
    }

    storageDeleteB64(file_id, callback) {
        this._storage('delete_b64', {
            'file_id': file_id,
        }, callback);
    }

    storageDownloadB64Chunk(file_id, callback) {
        this._storage('download_b64', {
            'file_id': file_id,
        }, callback);
    }

    storageUploadB64Chunk(parent_file_id, file_name, file_b64, read_groups, write_groups, callback) {
        this._storage('upload_b64', {
            'parent_file_id': parent_file_id,
            'file_name': file_name,
            'file_b64': file_b64,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }, callback);
    }

    storageDeleteFile(file_id, callback) {
        this.storageDeleteB64(file_id, callback);
    }

    storageDownloadFile(file_id, callback_file) {
        let self = this;
        var string_file_b64 = null;
        var file_name = 'file';
        function download(file_id, callback){
            self.storageDownloadB64Chunk(file_id, function (result) {
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

    storageUploadFile(bin, read_groups, write_groups, callback) {
        let self = this;
        function *div_chunks(text, n){
            for (var i = 0; i < text.length; i+= n){
                yield text.slice(i, i + n);
            }
        }
        var buff = Buffer.from(bin, 'utf8');
        let base64_data = buff.toString('base64');
        var raw_base64 = Buffer.from(base64_data, 'utf8');
        var base64_chunks = div_chunks(raw_base64, 1024 * 1024 * 4);
        var parent_file_id = null;
        let file_name = "file";
        function upload(parent_file_id, base64_chunk, callback){
            base64_chunk = base64_chunk.toString();
            self.storageUploadB64Chunk(parent_file_id, file_name, base64_chunk, read_groups, write_groups, function (data) {
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

    logCreateLog(event_source, event_name, event_param, callback) {
        this._log('create_log', {
            'event_source': event_source,
            'event_name': event_name,
            'event_param': event_param,
        }, callback);
    }

    logicRunFunction(function_name, payload, callback){
        this._logic('logic', {
            'function_name': function_name,
            'payload': payload,
        }, callback);
    }

}