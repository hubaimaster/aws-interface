import org.junit.jupiter.api.*;
import java.util.concurrent.Callable;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.awaitility.Awaitility.*;

public class AuthTest {
	static AWSInterface client = new AWSInterface("https://e3t7xfb981.execute-api.ap-northeast-2.amazonaws.com/prod_aws_interface/ipxsNKvdpXUgzAMqg2JgdM");
	String test_email = new String("ttest@gmail.com");
	String test_password = new String("ttestpassword");
	String new_email = new String("testwt123@gmail.com");
	String new_password = new String("test1451password");
	static String user_id = "jK5iK6UgYnTdaRhow5yvAT";
	static String guest_id = null;
	String fb_token = "EAAhNpAi3ZAqkBAKQGKSDG0wFZCgrd4LjAZCqGu0ZAqY8chIeishU2GFvmOAD6ZCTjLSg1NEPhtxmNqrp5Cb9BuamBVJEWzhnC5RcZAWwkr49Tgy8CjGwUEvEZBaZCniuS5L9fhZCSuscLATjvZAwRxdPuNTfxLOnE7MLaqr4TqBWaZA8QVpxumefK5U6xLZAtRN1QbXAVJZATAtz7zXZBPyrReru4nO4F7SkBlMaS5qIsfhmsc4AZDZD";
	String start_key = new String("0");
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
	
	//authRegiste is commented since it register same ID;
	/*
	//Test authRegister
	@Test
	public void authRegisterTest() {
		client.authRegister(new_email, new_password, (response, hasError)->{
            assertEquals(response.get("item").getAsJsonObject().get("email").getAsString(), new_email);
            received = true;	
	        });
		//wait until responseReceived turns into true;
		await().until(responseReceived());
	}
	 */
	
	// Test authGetUser
	@Test
	public void authGetUserTest() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.authGetUser(user_id, (response, hasError)->{
				assertEquals(response.get("item").getAsJsonObject().get("email").getAsString(), test_email);
				assertEquals(response.get("item").getAsJsonObject().get("id").getAsString(), user_id);
				received = true;
			});
		});
		//wait until responseReceived turns into true;
		await().until(responseReceived());
	}

	@Test
	public void authLogoutTest() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.authLogout((response, hasError)->{
	            assertNotNull(response.get("success"));
	            received = true;
	        });
		});
		//wait until responseReceived turns into true;
		await().until(responseReceived());
	}

	//Test loginFacebook
	@Test
	public void authLoginFacebookTest() {
		client.authLoginFacebook(fb_token, (response, hasError)->{
			assertNotNull(response.get("session_id"));
	        received = true;
		});
		//wait until responseReceived turns into true;
		await().until(responseReceived());
	}


	//Test authGetUsers with start_key
	@Test
	public void authGetUsers1Test() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.authGetUsers(start_key, (response, hasError)->{
				assertTrue(response.get("items").getAsJsonArray().isJsonArray());
	            received = true;
	        });
		});
		//wait until responseReceieved turns into true;
		await().until(responseReceived());
	}
	
	//Test authGetUsers without start_key
	@Test
	public void authGetUsers2Test() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.authGetUsers((response, hasError)->{
				assertTrue(response.get("items").getAsJsonArray().isJsonArray());
	            received = true;
	            });
			});
		//wait until responseReceived turns into true;
		await().until(responseReceived());
	}
	
	//test AuthGuest with guest_id
	@Test
	public void authGuest1Test() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.authGuest(guest_id,(response, hasError)->{
	            assertNotNull(response.get("session_id"));
	            received = true;
	            });
			});
		//wait until responseReceived turns into true;
		await().until(responseReceived());
	}
	
	@Test
	//test AuthGuest without guest_id
	public void authGuest2Test() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.authGuest((response, hasError)->{
	            assertNotNull(response.get("session_id"));
	            received = true;
	            });
			});
		//wait until responseReceived turns into true;
		await().until(responseReceived());
	}
	
}
