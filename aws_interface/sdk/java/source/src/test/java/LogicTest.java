import java.util.HashMap;
import org.junit.jupiter.api.*;
import java.util.concurrent.Callable;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.awaitility.Awaitility.*;

public class LogicTest {
	static AWSInterface client = new AWSInterface("https://e3t7xfb981.execute-api.ap-northeast-2.amazonaws.com/prod_aws_interface/ipxsNKvdpXUgzAMqg2JgdM");
	static String test_email = new String("ttest@gmail.com");
	static String test_password = new String("ttestpassword");
	static String test_function = new String("test-function");
	static HashMap<String, Object> test_payload = new HashMap<>();
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
	
	@Test
	public void logicRunFunctionTest() {
		test_payload.put("answer", 11);
		client.logicRunFunction(test_function, test_payload, (rr, hE)->{
        	System.out.println(rr);
        	assertEquals(rr.get("response").getAsJsonObject().get("answer").getAsInt(), 12);
        	received = true;
        });	
		await().until(responseReceived());
	}
}


