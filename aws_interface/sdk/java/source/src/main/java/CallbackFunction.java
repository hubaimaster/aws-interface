import com.google.gson.JsonObject;


public interface CallbackFunction {
    void callback(JsonObject response, boolean hasError);
}
