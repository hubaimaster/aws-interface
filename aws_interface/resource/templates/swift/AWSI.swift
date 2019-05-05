import Foundation

private class AWSINetworkRequest {

    private let session: URLSession = URLSession.shared

    func get(url: URL, completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void) {
        var request: URLRequest = URLRequest(url: url)
        request.httpMethod = "GET"
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        session.dataTask(with: request, completionHandler: completionHandler).resume()
    }

    func post(url: URL, body: NSMutableDictionary, completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void) throws {
        var request: URLRequest = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        request.httpBody = try JSONSerialization.data(withJSONObject: body, options: JSONSerialization.WritingOptions.prettyPrinted)
        session.dataTask(with: request, completionHandler: completionHandler).resume()
    }

}

class AWSI {

    private let baseUrl = "{{REST_API_URL}}"
    private var session_id: String?

    private func dataToJson(data: Data?)->[String: Any]?{
        guard let data = data else {
            return nil
        }
        do {
            if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String : Any]{
                return json
            }else{
                return nil
            }
        } catch {
            assertionFailure("[\(data)] cannot be converted to json format")
            return nil
        }
    }

    private func post(params: [String: Any], callback: @escaping (_ response: [String: Any]?, _ error: Error?)->Void){
        let request: AWSINetworkRequest = AWSINetworkRequest()
        if let url: URL = URL(string: baseUrl){
            let body: NSMutableDictionary = NSMutableDictionary()
            body.setDictionary(params)
            do{
                try request.post(url: url, body: body, completionHandler: { data, response, error in
                    callback(self.dataToJson(data: data), error)
                })
            }catch{
                callback(nil, nil)
            }
        }
    }

    private func callAPI(service_type: String, function_name: String, data: [String: Any], callback: @escaping (_ response: [String: Any]?)->Void){
        var data = data
        data["module_name"] = "cloud.\(service_type).\(function_name)"
        if let session_id = self.session_id{
            data["session_id"] = session_id
        }
        post(params: data) { (response, error) in
            var body: [String: Any] = [:]
            if let json = response, json.keys.contains("body"), let _body = json["body"] as? [String: Any]{
                body = _body
            }
            callback(body)
        }
    }

    private func auth(function_name: String, data: [String: Any], callback: @escaping (_ response: [String: Any]?)->Void){
        callAPI(service_type: "auth", function_name: function_name, data: data, callback: callback)
        self.log_create_log(event_source: "auth", event_name: function_name, event_param: nil) { (_) in }
    }

    private func database(function_name: String, data: [String: Any], callback: @escaping (_ response: [String: Any]?)->Void){
        callAPI(service_type: "database", function_name: function_name, data: data, callback: callback)
        self.log_create_log(event_source: "auth", event_name: function_name, event_param: nil) { (_) in }
    }

    private func storage(function_name: String, data: [String: Any], callback: @escaping (_ response: [String: Any]?)->Void){
        callAPI(service_type: "storage", function_name: function_name, data: data, callback: callback)
        self.log_create_log(event_source: "auth", event_name: function_name, event_param: nil) { (_) in }
    }

    private func logic(function_name: String, data: [String: Any], callback: @escaping (_ response: [String: Any]?)->Void){
        callAPI(service_type: "logic", function_name: function_name, data: data, callback: callback)
        self.log_create_log(event_source: "auth", event_name: function_name, event_param: nil) { (_) in }
    }

    private func log(function_name: String, data: [String: Any], callback: @escaping (_ response: [String: Any]?)->Void){
        callAPI(service_type: "log", function_name: function_name, data: data, callback: callback)
    }

    func auth_login(email: String, password: String, callback: @escaping (_ response: [String: Any]?)->Void){
        let data = [
            "email": email,
            "password": password,
        ]
        auth(function_name: "login", data: data) { (response) in
            if let json = response, json.keys.contains("session_id"), let session_id = json["session_id"] as? String{
                self.session_id = session_id
            }
            callback(response)
        }
    }

    func auth_register(email: String, password: String, extra: [String: Any]?, callback: @escaping (_ response: [String: Any]?)->Void){
        var data: [String: Any] = [
            "email": email,
            "password": password,
        ]
        if let extra = extra{
            data["extra"] = extra
        }
        auth(function_name: "register", data: data, callback: callback)
    }

    func auth_get_user(user_id: String, callback: @escaping (_ response: [String: Any]?)->Void){
        let data: [String: Any] = [
            "user_id": user_id,
        ]
        auth(function_name: "get_user", data: data, callback: callback)
    }

    func auth_logout(callback: @escaping (_ response: [String: Any]?)->Void){
        let data: [String: Any] = [:]
        self.session_id = nil
        auth(function_name: "logout", data: data, callback: callback)
    }

    func auth_guest(guest_id: String?=nil, callback: @escaping (_ response: [String: Any]?)->Void){
        var data: [String: Any] = [:]
        if let guest_id = guest_id{
            data["guest_id"] = guest_id
        }
        auth(function_name: "guest", data: data) { (response) in
            if let json = response, json.keys.contains("session_id"), let session_id = json["session_id"] as? String{
               self.session_id = session_id
            }
            callback(response)
        }
    }

    func database_create_item(item: [String: Any], partition: String, read_groups:[String], write_groups:[String], callback: @escaping (_ response: [String: Any]?)->Void){
        let data: [String: Any] = [
            "item": item,
            "partition": partition,
            "read_groups": read_groups,
            "write_groups": write_groups,
        ]
        database(function_name: "create_item", data: data, callback: callback)
    }

    func database_delete_item(item_id: String, callback: @escaping (_ response: [String: Any]?)->Void){
        let data: [String: Any] = [
            "item_id": item_id,
        ]
        database(function_name: "delete_item", data: data, callback: callback)
    }

    func database_get_item(item_id: String, callback: @escaping (_ response: [String: Any]?)->Void){
        let data: [String: Any] = [
            "item_id": item_id,
        ]
        database(function_name: "get_item", data: data, callback: callback)
    }

    func database_get_items(partition: String, start_key: [String: Any]?=nil, limit: Int=100, callback: @escaping (_ response: [String: Any]?)->Void){
        var data: [String: Any] = [
            "partition": partition,
            "limit": limit,
        ]
        if let start_key = start_key{
            data["start_key"] = start_key
        }
        database(function_name: "get_items", data: data, callback: callback)
    }

    func database_put_item_field(item_id: String, field_name: String, field_value: Any?, callback: @escaping (_ response: [String: Any]?)->Void){
        var data: [String: Any] = [
            "item_id": item_id,
            "field_name": field_name,
        ]
        if let field_value = field_value{
            data["field_value"] = field_value
        }
        database(function_name: "put_item_field", data: data, callback: callback)
    }

    func database_update_item(item_id: String, item: [String: Any], read_groups:[String], write_groups:[String], callback: @escaping (_ response: [String: Any]?)->Void){
        let data: [String: Any] = [
            "item_id": item_id,
            "item": item,
            "read_groups": read_groups,
            "write_groups": write_groups,
        ]
        database(function_name: "update_item", data: data, callback: callback)
    }

    /*
     query = [
        ["and|or", "field", "condition (eq|gt|..)", "value"], ...
    ]
    */
    func database_query_items(partition: String, query: [[String]], start_key: [String: Any]?, limit: Int=100, callback: @escaping (_ response: [String: Any]?)->Void){
        var data: [String: Any] = [
            "partition": partition,
            "query": query,
            "limit": limit,
        ]
        if let start_key = start_key{
            data["start_key"] = start_key
        }
        database(function_name: "query_items", data: data, callback: callback)
    }

    private func storage_delete_b64(file_id: String, callback: @escaping (_ response: [String: Any]?)->Void){
        let data: [String: Any] = [
            "file_id": file_id,
        ]
        storage(function_name: "delete_b64", data: data, callback: callback)
    }

    private func storage_download_b64(file_id: String, callback: @escaping (_ response: [String: Any]?)->Void){
        let data: [String: Any] = [
            "file_id": file_id,
        ]
        storage(function_name: "download_b64", data: data, callback: callback)
    }

    private func storage_upload_b64(parent_file_id: String?, file_name: String, file_b64: String, read_groups:[String], write_groups:[String], callback: @escaping (_ response: [String: Any]?)->Void){
        var data: [String: Any] = [
            "file_name": file_name,
            "file_b64": file_b64,
            "read_groups": read_groups,
            "write_groups": write_groups,
        ]
        if let parent_file_id = parent_file_id{
            data["parent_file_id"] = parent_file_id
        }
        storage(function_name: "upload_b64", data: data, callback: callback)
    }

    func storage_delete_file(file_id: String, callback: @escaping (_ response: [String: Any]?)->Void){
        storage_delete_b64(file_id: file_id, callback: callback)
    }

    func storage_download_file(_file_id: String, callback: @escaping (Data?)->Void){
        func download(file_id: String, stringFileBase64: String){
            storage_download_b64(file_id: file_id) { (response) in
                if let response = response{
                    let stringFileBase64Chunk = response["file_b64"] as! String + stringFileBase64
                    if response.keys.contains("parent_file_id"){
                        if let parent_file_id = response["parent_file_id"] as? String{
                            download(file_id: parent_file_id, stringFileBase64: stringFileBase64Chunk)
                        }
                    }else{
                        let data = Data(base64Encoded: stringFileBase64Chunk)
                        callback(data)
                    }
                }else{
                    //No Response
                    callback(nil)
                }
            }
        }
        download(file_id: _file_id, stringFileBase64: "")
    }

    func storage_upload_file(file_data: Data, file_name: String, read_groups: [String], write_groups: [String], callback: @escaping (_ response: [String: Any]?)->Void){
        let rawBase64String = file_data.base64EncodedString()
        let stringChunks = rawBase64String.split(by: 1024 * 1024 * 5)

        func upload(count: Int, parent_file_id: String?){
            let b64String = stringChunks[count]
            storage_upload_b64(parent_file_id: parent_file_id, file_name: file_name, file_b64: b64String, read_groups: read_groups, write_groups: write_groups) { (response) in
                if let response = response, response.keys.contains("file_id"), let file_id = response["file_id"] as? String{
                    if count + 1 < stringChunks.count{
                        upload(count: count + 1, parent_file_id: file_id)
                    }else{
                        callback(response)
                    }
                }else{
                    callback(nil)
                }
            }
        }
    }

    func log_create_log(event_source: String, event_name: String, event_param: [String: Any]?, callback: @escaping (_ response: [String: Any]?)->Void){
        var data: [String: Any] = [
            "event_source": event_source,
            "event_name": event_name,
        ]
        if let event_param = event_param{
            data["event_param"] = event_param
        }
        log(function_name: "create_log", data: data, callback: callback)
    }

}

extension String {
    func split(by length: Int) -> [String] {
        var startIndex = self.startIndex
        var results = [Substring]()

        while startIndex < self.endIndex {
            let endIndex = self.index(startIndex, offsetBy: length, limitedBy: self.endIndex) ?? self.endIndex
            results.append(self[startIndex..<endIndex])
            startIndex = endIndex
        }

        return results.map { String($0) }
    }
}
