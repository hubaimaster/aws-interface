var awsi = (function () {
  var apiInstance;

  function create () {
    document.write("<script src='jquery.min.js'></script>");
    var manifest = null;
    $.getJSON('manifest.json', function(data) {
        alert(data);
        manifest = data;
    });

    function _request(method, url, data, success){
      if (getSessionId() != null){
        data['session_id'] = getSessionId();
      }
      $.ajax({
        method : method,
        url : url,
        data: data,
        success : success,
        error : function(e) {
            //alert("error: " + JSON.stringify(e));
        }
      });
    }

    function _get(url, data, success){
      _request("GET", url, data, success);
    }

    function _post(url, data, success){
      _request("POST", url, data, success);
    }

    function _get_rest_api_url(recipe_key){
      var url = manifest[recipe_key]['rest_api_url'];
      return url;
    }
    
    function _auth(api_name, data, success) {
      var api_url = _get_rest_api_url('auth');
      data['cloud_api_name'] = api_name;
      _post(api_url, data, success);
    }

    function _database(api_name, data, success) {
      var api_url = _get_rest_api_url('database');
      data['cloud_api_name'] = api_name;
      _post(api_url, data, success);
    }

    function _storage(api_name, data, success) {
      var api_url = _get_rest_api_url('storage');
      data['cloud_api_name'] = api_name;
      _post(api_url, data, success);
    }

    function hasSession(){
      var session_id = getSessionId();
      if (session_id == null || session_id.length == 0){
        return false;
      }else{
        return true;
      }
    }

    function setCookie(name, value, days) {
      var expires = "";
      if (days) {
          var date = new Date();
          date.setTime(date.getTime() + (days*24*60*60*1000));
          expires = "; expires=" + date.toUTCString();
      }
      document.cookie = name + "=" + (value || "")  + expires + "; path=/";
    }

    function getCookie(name) {
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for(var i=0;i < ca.length;i++) {
            var c = ca[i];
            while (c.charAt(0)==' ') c = c.substring(1,c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
        }
        return null;
    }

    function eraseCookie(name) {
        document.cookie = name+'=; Max-Age=-99999999;';
    }

    function getSessionId(){
      var session_id = getCookie('session_id');
      return session_id;
    }

    function login(email, password, callback){
        _auth('login', {
            email: email,
            password: password,
        }, function (response) {
            setCookie('session_id', response.item.session_id, 1);
            callback(response);
        });
    }

    function logout(callback){
        _auth('logout', {

        }, function (response) {
            eraseCookie('session_id');
            callback(response);
        });
    }

    function register(email, password, callback){
        _auth('register', {
            email: email,
            password: password,
        }, function (response) {
            callback(response);
        });
    }

    function guest(guest_id, callback){
        _auth('guest', {
            guest_id: guest_id,
        }, function (response) {
            callback(response);
        });
    }

    function get_user(user_id, callback) {
        _auth('get_user', {
            user_id: user_id,
        }, function (response) {
            callback(response);
        });
    }

    function set_user(user_id, field_pairs, callback) {
        _auth('set_user', {
            user_id: user_id,
            field_pairs: field_pairs,
        }, function (response) {
            callback(response);
        });
    }
    
    function create_item(partition, item, read_permissions, write_permissions, callback) {
        _database('create_item', {
            item: item,
            partition: partition,
            read_permissions: read_permissions,
            write_permissions: write_permissions,
        }, function (response) {
            callback(response);
        });
    }

    function delete_item(item_id, callback) {
        _database('delete_item', {
            item_id: item_id,
        }, function (response) {
            callback(response);
        });
    }

    function get_item(item_id, callback) {
        _database('get_item', {
            item_id: item_id,
        }, function (response) {
            callback(response);
        });
    }
    
    function get_items(partition, callback) {
        _database('get_items', {
            partition: partition    
        }, function (response) {
            callback(response);
        });
    }

    function put_item_field(item_id, field_name, field_value, callback) {
        _database('put_item_field', {
            item_id: item_id,
            field_name: field_name,
            field_value: field_value,
        }, function (response) {
            callback(response);
        });
    }

    function update_item(item_id, item, read_groups, write_groups, callback) {
        _database('update_item', {
            item_id: item_id,
            item: item,
            read_groups: read_groups,
            write_groups: write_groups,
        }, function (response) {
            callback(response);
        });
    }

    function create_folder(parent_path, folder_name, read_groups, write_groups, callback) {
        _storage('create_folder', {
            parent_path: parent_path,
            folder_name: folder_name,
            read_groups: read_groups,
            write_groups: write_groups,
        }, function (response) {
            callback(response);
        });
    }

    function delete_path(path, callback) {
        _storage('delete_path', {
            path: path,
        }, function (response) {
            callback(response);
        });
    }
    
    function download_file(file_path, callback) {
        _storage('download_file', {
            file_path: file_path,
        }, function (response) {
            callback(response);
        });
    }

    function get_folder_list(path, start_key, callback) {
        _storage('get_folder_list', {
            path: path,
            start_key: start_key,
        }, function (response) {
            callback(response);
        });
    }

    function upload_file(parent_path, file_bin, file_name, read_groups, write_groups, callback) {
        var formData = new FormData();
        formData.append('file_bin', file_bin);
        formData.append('parent_path', parent_path);
        formData.append('file_name', file_name);
        formData.append('read_groups', JSON.stringify(read_groups));
        formData.append('write_groups', JSON.stringify(write_groups));
        _storage('upload_file', formData, function (response) {
            callback(response);
        });
    }

    return {
        hasSession: hasSession,
        auth: {
            login: login,
            logout: logout,
            register: register,
            guest: guest,
            get_user: get_user,
            set_user: set_user,
        },
        database: {
            create_item: create_item,
            delete_item: delete_item,
            get_item: get_item,
            get_items: get_items,
            put_item_field: put_item_field,
            update_item: update_item,
        },
        storage: {
            create_folder: create_folder,
            delete_path: delete_path,
            download_file: download_file,
            get_folder_list: get_folder_list,
            upload_file: upload_file,
        },
    };
  }

  return {
    getInstance: function() {
      if(!apiInstance) {
        apiInstance = create();
      }
      return apiInstance;
    }
  };

  function Singleton () {
    if(!apiInstance) {
      apiInstance = intialize();
    }
  };

})();