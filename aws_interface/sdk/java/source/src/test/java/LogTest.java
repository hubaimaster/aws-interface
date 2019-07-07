import java.util.HashMap;
import static org.junit.jupiter.api.Assertions.assertNotNull;

public class LogTest {
	static AWSInterface client = new AWSInterface("https://e3t7xfb981.execute-api.ap-northeast-2.amazonaws.com/prod_aws_interface/ipxsNKvdpXUgzAMqg2JgdM");
	static String test_email = new String("ttest@gmail.com");
	static String test_password = new String("ttestpassword");
	static String test_source = new String("test-source");
	static String test_name = new String("test-name");
	static String test_param = new String("test-param");
	
	static public void logCreateLogTest() {
        client.logCreateLog(test_source, test_name, test_param, (response, hasError)->{
        	System.out.println(response);
        	assertNotNull(response.get("success"));
        });
		
	}
	 public static void main(String[] args) {

		 client.authLogin(test_email, test_password, (response, hasError)->{
	            System.out.println(response);
	            logCreateLogTest();
	        });
	 }
}


