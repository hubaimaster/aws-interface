import org.junit.jupiter.api.*;
import java.util.concurrent.Callable;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.awaitility.Awaitility.*;

public class LogTest {
	static AWSInterface client = new AWSInterface("https://e3t7xfb981.execute-api.ap-northeast-2.amazonaws.com/prod_aws_interface/ipxsNKvdpXUgzAMqg2JgdM");
	static String test_email = new String("ttest@gmail.com");
	static String test_password = new String("ttestpassword");
	static String test_source = new String("test-source");
	static String test_name = new String("test-name");
	static String test_param = new String("test-param");
	boolean received = false;
	
	//Declare Callable object for check if the response is received;
	private Callable<Boolean> responseReceived(){
		return new Callable<Boolean>() {
			public Boolean call() throws Exception{
				return received;
			}
		};
	}
	
	// Before each testcase, initialize received flag with false to use awaitility for async testing
	@BeforeEach
	public void initialiize() {
		received = false;
	}
	
	// Test creating log
	@Test
	public void logCreateLogTest() {
		client.authLogin(test_email, test_password, (rr, hE)->{
	        client.logCreateLog(test_source, test_name, test_param, (response, hasError)->{
	        	System.out.println(response);
	        	assertNotNull(response.get("success").getAsString());
	        	received = true;
	        });
		});
		//wait until responseReceived turns into true;
		await().until(responseReceived());
	}

}


