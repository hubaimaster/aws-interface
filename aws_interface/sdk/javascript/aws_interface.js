
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

    isLogin(){
        return this.get_session_id() != null;
    }

    get_session_id(){
        return window.localStorage.getItem('session_id');
    }

    set_session_id(session_id){
        window.localStorage.setItem('session_id', session_id);
    }

    remove_session(){
        window.localStorage.removeItem('session_id');
    }

    static _get(object, key, defaultValue=null) {
        var result = object[key];
        return (typeof result !== "undefined") ? result : defaultValue;
    }

    callAPI(module_name, data) {
        self = this;
        if (data == null){
            data = {};
        }
        data['module_name'] = module_name;
        if (this.get_session_id() != null){
            data['session_id'] = this.get_session_id();
        }
        return new Promise(function (resolve, reject) {
            self._post(self.getBaseUrl(), data, function (body) {
                if ("error" in body){
                    reject(new Error(body["error"]));
                }else{
                    resolve(body);
                }
            });
        });
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

    _auth(api_name, data) {
        return this.callAPI('cloud.auth.' + api_name, data);
    }

    _database(api_name, data) {
        return this.callAPI('cloud.database.' + api_name, data);
    }

    _storage(api_name, data) {
        return this.callAPI('cloud.storage.' + api_name, data);
    }

    _logic(api_name, data) {
        return this.callAPI('cloud.logic.' + api_name, data);
    }

    _log(api_name, data) {
        return this.callAPI('cloud.log.' + api_name, data);
    }

    authRegister(email, password, extra) {
        return this._auth('register', {
            'email': email,
            'password': password,
            'extra': extra,
        });
    }

    authLogin(email, password) {
        let self = this;
        return new Promise((resolve, reject) => {
            this._auth('login', {
                'email': email,
                'password': password,
            }).then(function (body) {
                self.set_session_id(Client._get(body,'session_id'));
                resolve(body);
            }).catch(reject);
        });
    }

    authLoginFacebook(access_token) {
        let self = this;
        return new Promise((resolve, reject) => {
            this._auth('login_facebook', {
                'access_token': access_token,
            }).then(function (body) {
                self.set_session_id(Client._get(body,'session_id'));
                resolve(body);
            }).catch(reject);
        });
    }

    authGetUser(user_id) {
        return this._auth('get_user', {
            'user_id': user_id,
        });
    }

    authGetMe() {
        return this._auth('get_me', {

        });
    }

    authGetUsers(start_key=null) {
        return this._auth('get_users', {
            'start_key': start_key,
        });
    }

    authLogout() {
        const self = this;
        return new Promise((resolve, reject) => {
            self._auth('logout', {
                'session_id': self.get_session_id(),
            }).then(function (data) {
                self.remove_session();
                resolve(data);
            }).catch(function (data) {
                self.remove_session();
                reject(data);
            });
        });
    }

    authGuest(guest_id=null) {
        let self = this;
        return new Promise((resolve, reject) => {
            this._auth('guest', {
                'guest_id': guest_id,
            }).then(function (body) {
                self.set_session_id(Client._get(body,'session_id'));
                resolve(body);
            }).catch(reject);
        });
    }

    databaseCreateItem(partition, item) {
        return this._database('create_item', {
            'item': item,
            'partition': partition,
        });
    }

    databaseDeleteItem(item_id) {
        return this._database('delete_item', {
            'item_id': item_id,
        });
    }

    databaseGetItem(item_id) {
        return this._database('get_item', {
            'item_id': item_id,
        });
    }

    databaseGetItemCount(partition, field=null, value=null) {
        return this._database('get_item_count', {
            'partition': partition,
            'field': field,
            'value': value,
        });
    }

    databaseGetItems(partition, start_key=null, limit=100) {
        return this._database('get_items', {
            'partition': partition,
            'start_key': start_key,
            'limit': limit,
        });
    }

    databasePutItemField(item_id, field_name, field_value) {
        return this._database('put_item_field', {
            'item_id': item_id,
            'field_name': field_name,
            'field_value': field_value,
        });
    }

    databaseUpdateItem(item_id, item) {
        return this._database('update_item', {
            'item_id': item_id,
            'item': item,
        });
    }

    databaseQueryItems(partition, query, start_key=null, limit=100, reverse=false) {
        return this._database('query_items', {
            'partition': partition,
            'query': query,
            'start_key': start_key,
            'limit': limit,
            'reverse': reverse,
        });
    }

    storageDeleteB64(file_id) {
        return this._storage('delete_b64', {
            'file_id': file_id,
        });
    }

    storageDownloadB64Chunk(file_id) {
        return this._storage('download_b64', {
            'file_id': file_id,
        });
    }

    storageUploadB64Chunk(parent_file_id, file_name, file_b64) {
        return this._storage('upload_b64', {
            'parent_file_id': parent_file_id,
            'file_name': file_name,
            'file_b64': file_b64,
        });
    }

    storageDeleteFile(file_id) {
        return this.storageDeleteB64(file_id);
    }

    storageDownloadFile(file_id) {
        let self = this;
        var string_file_b64 = null;
        var file_name = 'file';
        function download(file_id, callback){
            self.storageDownloadB64Chunk(file_id).then(function (result) {
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
        return new Promise((resolve, reject) => {
            download(file_id, function (string_file_b64, result) {
                if (string_file_b64 == null){
                    callback_file(null);
                    console.error(result);
                    reject(new Error(result))
                }else{
                    let file_bin = Buffer.from(string_file_b64, 'base64');
                    resolve(file_bin);
                }
            });
        });
    }

    storageUploadFile(bin) {
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
            self.storageUploadB64Chunk(parent_file_id, file_name, base64_chunk).then(function (data) {
                var parent_file_id = data['file_id'];
                var next_base64_chunk = base64_chunks.next();
                if (next_base64_chunk.done){
                    callback(data);
                }else{
                    upload(parent_file_id, next_base64_chunk.value, callback);
                }
            });
        }
        return new Promise((resolve) => {
            upload(parent_file_id, base64_chunks.next().value, function (data) {
                resolve(data);
            });
        });
    }

    logCreateLog(event_source, event_name, event_param) {
        return this._log('create_log', {
            'event_source': event_source,
            'event_name': event_name,
            'event_param': event_param,
        });
    }

    logGetLogs(event_source, event_name, log_owner, start_key, reverse){
        return this._log('get_logs', {
            "event_name": event_name,
            "event_source": event_source,
            "reverse": reverse,
            "start_key": start_key,
            "user_id": log_owner
        });
    }

    logicRunFunction(function_name, payload){
        return this._logic('run_function', {
            'function_name': function_name,
            'payload': payload,
        });
    }

}