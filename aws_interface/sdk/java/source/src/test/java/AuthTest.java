import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertNotNull;

public class AuthTest {
	static AWSInterface client = new AWSInterface("https://e3t7xfb981.execute-api.ap-northeast-2.amazonaws.com/prod_aws_interface/ipxsNKvdpXUgzAMqg2JgdM");
	String test_email = new String("ttest@gmail.com");
	String test_password = new String("ttestpassword");
	static String user_id = null;
	static String guest_id = null;
	String fb_token = "";
	String start_key = new String("0");
	

	@BeforeAll
	public static void authRegisterTest() {
		client.authRegister("example@email.com", "examplepassword", (response, hasError)->{
			user_id = response.get("item").getAsJsonObject().get("id").getAsString();
			guest_id = user_id;
			System.out.println(response);
            System.out.println(hasError);
	        });
	}
	
	@BeforeEach
	public void setUp() {
        client.authLogin(test_email, test_password, (response, hasError)->{
            System.out.println(response);
        });
	}
	
	@AfterEach
	public void tearDown() {
		client.authLogout((response, hasError)->{
            System.out.println(response);
        });
	}	
	
	@Test
	public void authGetUserTest() {
		 client.authGetUser(user_id, (response, hasError)->{
			 System.out.println(response);
	         System.out.println(hasError);
	         assertEquals(response.get("item").getAsJsonObject().get("email").getAsString(), test_email);
			 assertEquals(response.get("item").getAsJsonObject().get("id").getAsString(), user_id);
	        });
	}

	@Test
	public void authLoginFacebookTest() {
		 client.authLoginFacebook(fb_token, (response, hasError)->{
			 System.out.println(response);
	         System.out.println(hasError);
	         assertNotNull(response.get("session_id"));
	        });
	}

	@Test
	public void authGetUsers1Test() {
		 client.authGetUsers(start_key, (response, hasError)->{
	            System.out.println(response);
	            System.out.println(hasError);
	            assertTrue(response.get("items").getAsJsonArray().isJsonArray());
	        });
	}
	
	@Test
	public void authGetUsers2Test() {
		 client.authGetUsers((response, hasError)->{
	            System.out.println(response);
	            System.out.println(hasError);
	            assertTrue(response.get("items").getAsJsonArray().isJsonArray());
	        });
	}
	
	@Test
	public void authGuest1Test() {
		 client.authGuest(guest_id,(response, hasError)->{
	            System.out.println(response);
	            assertNotNull(response.get("session_id"));
	        });
	}
	
	@Test
	public void authGuest2Test() {
		 client.authGuest((response, hasError)->{
	            System.out.println(response);
	            assertNotNull(response.get("session_id"));
	        });
	}

}
