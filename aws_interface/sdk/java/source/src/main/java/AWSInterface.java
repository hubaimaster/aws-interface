

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import okhttp3.*;


public final class AWSInterface {
    private String endpointUrl = "{{REST_API_URL}}";
    private String sessionId = null;
    private final OkHttpClient client = new OkHttpClient();
    private static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

    AWSInterface(String endpointUrl){
        this.endpointUrl = endpointUrl;
    }

    AWSInterface(){}

    private void post(String url, String json, CallbackFunction callbackFunction) {
        RequestBody body = RequestBody.create(JSON, json);
        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                e.printStackTrace();
                callbackFunction.callback(null, true);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                try (ResponseBody responseBody = response.body()) {
                    if (response.isSuccessful()){
                        JsonObject jsonResponse = new Gson().fromJson(responseBody.string(), JsonObject.class);
                        boolean hasError = jsonResponse.has("error");
                        callbackFunction.callback(jsonResponse, hasError);
                    }else{
                        callbackFunction.callback(null, true);
                    }
                }
            }
        });
    }

    private void callAPI(String serviceType, String functionName, HashMap<String, Object> data, CallbackFunction callbackFunction){
        String module_name = "cloud." + serviceType + "." + functionName;
        data.put("session_id", sessionId);
        data.put("module_name", module_name);
        String json = new Gson().toJson(data);
        post(endpointUrl, json, ((response, hasError) -> {
            if (response.has("body")){
                callbackFunction.callback(response.get("body").getAsJsonObject(), hasError);
            }else{
                callbackFunction.callback(null, true);
            }
        }));
    }

    private void auth(String apiName, HashMap<String, Object> data, CallbackFunction callbackFunction){
        callAPI("auth", apiName, data, callbackFunction);
    }

    private void database(String apiName, HashMap<String, Object> data, CallbackFunction callbackFunction){
        callAPI("database", apiName, data, callbackFunction);
    }

    private void storage(String apiName, HashMap<String, Object> data, CallbackFunction callbackFunction){
        callAPI("storage", apiName, data, callbackFunction);
    }

    private void logic(String apiName, HashMap<String, Object> data, CallbackFunction callbackFunction){
        callAPI("logic", apiName, data, callbackFunction);
    }

    private void log(String apiName, HashMap<String, Object> data, CallbackFunction callbackFunction){
        callAPI("log", apiName, data, callbackFunction);
    }

    public void authRegister(String email, String password, HashMap<String, Object> extra, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("email", email);
        data.put("password", password);
        data.put("extra", extra);
        auth("register", data, callbackFunction);
    }

    public void authRegister(String email, String password, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("email", email);
        data.put("password", password);
        auth("register", data, callbackFunction);
    }

    public void authLogin(String email, String password, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("email", email);
        data.put("password", password);
        auth("login", data, ((response, hasError) -> {
            if (response.has("session_id")){
                this.sessionId = response.get("session_id").getAsString();
            }
            callbackFunction.callback(response, hasError);
        }));
    }

    public void authGetUser(String userId, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("user_id", userId);
        auth("get_user", data, callbackFunction);
    }

    public void authGetUsers(String startKey, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("start_key", startKey);
        auth("get_users", data, callbackFunction);
    }

    public void authGetUsers(CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        auth("get_users", data, callbackFunction);
    }

    public void authLogout(CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("session_id", sessionId);
        auth("logout", data, callbackFunction);
    }

    public void authGuest(String guestId, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("guest_id", guestId);
        auth("guest", data, ((response, hasError) -> {
            if (response.has("session_id")){
                this.sessionId = response.get("session_id").getAsString();
            }
            callbackFunction.callback(response, hasError);
        }));
    }

    public void authGuest(CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        auth("guest", data, ((response, hasError) -> {
            if (response.has("session_id")){
                this.sessionId = response.get("session_id").getAsString();
            }
            callbackFunction.callback(response, hasError);
        }));
    }

    public void databaseCreateItem(HashMap<String, Object> item, String partition, ArrayList<String> readGroups, ArrayList<String> writeGroups, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("item", item);
        data.put("partition", partition);
        data.put("read_groups", readGroups);
        data.put("write_groups", writeGroups);
        database("create_item", data, callbackFunction);
    }

    public void databaseCreateItem(HashMap<String, Object> item, String partition, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("item", item);
        data.put("partition", partition);
        database("create_item", data, callbackFunction);
    }

    public void databaseDeleteItem(String itemId, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("item_id", itemId);
        database("delete_item", data, callbackFunction);
    }

    public void databaseGetItem(String itemId, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("item_id", itemId);
        database("get_item", data, callbackFunction);
    }

    public void databaseGetItems(String partition, String startKey, int limit, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("partition", partition);
        data.put("start_key", startKey);
        data.put("limit", limit);
        database("get_items", data, callbackFunction);
    }

    public void databaseGetItems(String partition, int limit, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("partition", partition);
        data.put("limit", limit);
        database("get_items", data, callbackFunction);
    }

    public void databasePutItemField(String itemId, String fieldName, Object fieldValue, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("item_id", itemId);
        data.put("field_name", fieldName);
        data.put("field_value", fieldValue);
        database("put_item_field", data, callbackFunction);
    }

    public void databaseUpdateItem(String itemId, HashMap<String, Object> item, ArrayList<String> readGroups, ArrayList<String> writeGroups, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("item_id", itemId);
        data.put("item", item);
        data.put("read_groups", readGroups);
        data.put("write_groups", writeGroups);
        database("update_item", data, callbackFunction);
    }

    public void databaseUpdateItem(String itemId, HashMap<String, Object> item, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("item_id", itemId);
        data.put("item", item);
        database("update_item", data, callbackFunction);
    }

    public void databaseQueryItems(String partition, ArrayList<HashMap<String, Object>> query, String startKey, int limit, boolean reverse, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("partition", partition);
        data.put("query", query);
        data.put("start_key", startKey);
        data.put("limit", limit);
        data.put("reverse", reverse);
        database("query_items", data, callbackFunction);
    }

    public void databaseQueryItems(String partition, ArrayList<HashMap<String, Object>> query, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("partition", partition);
        data.put("query", query);
        data.put("limit", 100);
        data.put("reverse", false);
        database("query_items", data, callbackFunction);
    }

    public void storageDeleteB64(String fileId, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("file_id", fileId);
        storage("delete_b64", data, callbackFunction);
    }

    public void storageDownloadB64(String fileId, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("file_id", fileId);
        storage("download_b64", data, callbackFunction);
    }

    private void storageUploadB64(String parentFileId, String fileName, String fileB64, ArrayList<String> readGroups, ArrayList<String> writeGroups, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        if (parentFileId != null){
            data.put("parent_file_id", parentFileId);
        }
        if (fileName != null){
            data.put("file_name", fileName);
        }
        data.put("file_b64", fileB64);
        data.put("read_groups", readGroups);
        data.put("write_groups", writeGroups);
        storage("upload_b64", data, callbackFunction);
    }

    private void storageUploadB64(String parentFileId, String fileName, String fileB64, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        if (parentFileId != null){
            data.put("parent_file_id", parentFileId);
        }
        if (fileName != null){
            data.put("file_name", fileName);
        }
        data.put("file_name", fileName);
        data.put("file_b64", fileB64);
        storage("upload_b64", data, callbackFunction);
    }

    public void storageDeleteFile(String fileId, CallbackFunction callbackFunction){
        storageDeleteB64(fileId, callbackFunction);
    }

    private byte[] decodeBase64String(String base64String){
        byte[] stringBytes = base64String.getBytes(StandardCharsets.UTF_8);
        byte[] bytes = java.util.Base64.getDecoder().decode(stringBytes);
        return bytes;
    }

    private void downloadFileChunks(String fileId, ArrayList<String> chunks, CallbackFunction callbackFunction, CallbackFileByteFunction callbackFileByteFunction){
        storageDownloadB64(fileId, ((response, hasError) -> {
            if (response.has("file_b64")){
                chunks.add(0, response.get("file_b64").getAsString());
            }
            if (response.has("parent_file_id")){
                String nextFileId = response.get("parent_file_id").getAsString();
                downloadFileChunks(nextFileId, chunks, callbackFunction, callbackFileByteFunction);
            }else{
                String b64String = String.join("", chunks);
                byte[] fileBytes = this.decodeBase64String(b64String);
                callbackFunction.callback(response, hasError);
                callbackFileByteFunction.callback(fileBytes);
            }
        }));
    }

    public void storageDownloadFileByte(String fileId, CallbackFunction callbackFunction, CallbackFileByteFunction callbackFileByteFunction){
        ArrayList<String> chunks = new ArrayList<>();
        downloadFileChunks(fileId, chunks, callbackFunction, callbackFileByteFunction);
    }

    private byte[] readFileBytes(File file) throws IOException {
        ByteArrayOutputStream ous = null;
        InputStream ios = null;
        try {
            byte[] buffer = new byte[4096];
            ous = new ByteArrayOutputStream();
            ios = new FileInputStream(file);
            int read = 0;
            while ((read = ios.read(buffer)) != -1) {
                ous.write(buffer, 0, read);
            }
        }finally {
            if (ous != null) ous.close();
            if (ios != null) ios.close();
        }
        return ous.toByteArray();
    }

    private String fileToBase64(File file) throws IOException{
        byte[] fileBytes = readFileBytes(file);
        byte[] encoded = Base64.getEncoder().encode(fileBytes);
        return new String(encoded, StandardCharsets.UTF_8);
    }

    private static Collection<String> splitStringBySize(String str, int size) {
        ArrayList<String> split = new ArrayList<>();
        for (int i = 0; i <= str.length() / size; i++) {
            split.add(str.substring(i * size, Math.min((i + 1) * size, str.length())));
        }
        return split;
    }

    private void uploadFileChunks(String parentFileId, String fileName, Iterator<String> chunks, ArrayList<String> readGroups, ArrayList<String> writeGroups, CallbackFunction callbackFunction){
        storageUploadB64(parentFileId, fileName, chunks.next(), readGroups, writeGroups, ((response, hasError) -> {
            if (chunks.hasNext()){
                String fileId = response.get("file_id").getAsString();
                this.uploadFileChunks(fileId, fileName, chunks, readGroups, writeGroups, callbackFunction);
            }else{
                callbackFunction.callback(response, hasError);
            }
        }));
    }

    public void storageUploadFile(File file, ArrayList<String> readGroups, ArrayList<String> writeGroups, CallbackFunction callbackFunction) throws IOException{
        String b64String = fileToBase64(file);
        int size = 4 * 10000; // 4 mb
        Iterator<String> chunks = splitStringBySize(b64String, size).iterator();
        uploadFileChunks(null, file.getName(), chunks, readGroups, writeGroups, callbackFunction);
    }

    public void logicRunFunction(String functionName, HashMap<String, Object> payload, CallbackFunction callbackFunction){
        HashMap<String, Object> data = new HashMap<>();
        data.put("function_name", functionName);
        data.put("payload", payload);
        logic("run_function", data, callbackFunction);
    }

    public static void main(String... args) throws Exception {
        String url = "https://r9ed0xv21m.execute-api.ap-northeast-2.amazonaws.com/prod_aws_interface/JwkVPTs2qXuWMD5XSk2zSN";
        AWSInterface awsinterface = new AWSInterface(url);
        awsinterface.authLogin("kchdully@naver.com", "pass1234", ((response, hasError) -> {
            System.out.println(response);

            ClassLoader classLoader = awsinterface.getClass().getClassLoader();
            File file = new File(classLoader.getResource("postman.zip").getFile());

            ArrayList<String> readGroups = new ArrayList<>();
            readGroups.add("owner");

            ArrayList<String> writeGroups = new ArrayList<>();
            writeGroups.add("owner");

            try {
                awsinterface.storageUploadFile(file, readGroups, writeGroups, (response2, hasError2)->{
                    System.out.println(response2);
                });
            } catch (IOException e) {
                e.printStackTrace();
            }

        }));

    }
}