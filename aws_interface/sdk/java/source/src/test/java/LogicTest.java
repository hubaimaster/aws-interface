import java.util.HashMap;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class LogicTest {
	static AWSInterface client = new AWSInterface("https://e3t7xfb981.execute-api.ap-northeast-2.amazonaws.com/prod_aws_interface/ipxsNKvdpXUgzAMqg2JgdM");
	static String test_email = new String("ttest@gmail.com");
	static String test_password = new String("ttestpassword");
	static String test_function = new String("test-function");
	static HashMap<String, Object> test_payload = new HashMap<>();
	
	static public void logicRunFunctionTest() {
		 test_payload.put("answer", 11);
        client.logicRunFunction(test_function, test_payload, (rr, hE)->{
        	System.out.println(rr);
        	assertEquals(rr.get("response").getAsJsonObject().get("answer").getAsInt(), 12);
        });
		
	}
	 public static void main(String[] args) {

		 client.authLogin(test_email, test_password, (response, hasError)->{
	            System.out.println(response);
	            logicRunFunctionTest();

	        });
	 }
}


