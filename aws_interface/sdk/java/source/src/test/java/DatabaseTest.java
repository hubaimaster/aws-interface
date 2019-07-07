import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.HashMap;

public class DatabaseTest {
	static AWSInterface client = new AWSInterface("https://e3t7xfb981.execute-api.ap-northeast-2.amazonaws.com/prod_aws_interface/ipxsNKvdpXUgzAMqg2JgdM");
	static String test_email = new String("ttest@gmail.com");
	static String test_password = new String("ttestpassword");
	String test_partition = new String("test-partition");
    String count_field = new String("readGroups");
    String count_value = new String("[\"owner\"]");
    String put_field = new String("test-field");
    String put_value = new String("test-value");
	static HashMap<String, Object> test_item = new HashMap<>();
	static HashMap<String, Object> test_item_new = new HashMap<>();
    static ArrayList<String> readGroups = new ArrayList<>();
	static ArrayList<String> writeGroups = new ArrayList<>();
	static ArrayList<HashMap<String, Object>> query = new ArrayList<>();
	String item_id = null;
	String start_key = "0";
	int limit = 10;
	boolean reverse = false;

	@BeforeAll
	public static void LoginSDK() {
		test_item.put("test-item", "test-value");
		test_item_new.put("creation_time", 1);
        readGroups.add("owner");
        writeGroups.add("owner");
    	HashMap<String, Object> hm = new HashMap<>();
    	hm.put("option","or");
    	hm.put("field", "partition");
    	hm.put("condition","eq");
    	hm.put("value", "test-partition");
    	query.add(hm);
		client.authLogin(test_email, test_password, (response, hasError)->{
            System.out.println(response);
        });
	}
	
	@AfterAll
	public void LogoutSDK() {
		client.authLogout((response, hasError)->{
            System.out.println(response);
        });
	}	

	@BeforeEach
	public void databaseCreateItemTest() {
		client.databaseCreateItem(test_partition, test_item, (response, hasError)->{
			System.out.println(response);
			System.out.println(hasError);
			assertNotNull(response.get("item_id"));
			item_id = response.get("item_id").getAsString();
        });
	}
	
	@AfterEach
	public void databaseDeleteItemTest() {
		client.databaseDeleteItem(item_id, (response, hasError)->{
			System.out.println(response);
			System.out.println(hasError);
			assertNotNull(response.get("item_id"));
        });
	}

	@Test
	public void databaseCreateItem2Test() {
		client.databaseCreateItem(test_partition, test_item, readGroups, writeGroups, (response, hasError)->{
			System.out.println(response);
	        System.out.println(hasError);
         	assertNotNull(response.get("item_id"));
	        });
	}

	@Test
	public void databaseGetItemTest() {
		 client.databaseGetItem(item_id, (response, hasError)->{
			System.out.println(response);
	        System.out.println(hasError);
	        //Need something here
	        //assertNotNull(response.get("items").getAsJsonArray());
	        });
	}
	
	@Test
	public void databaseGetItemCount1Test() {
		 client.databaseGetItemCount(test_partition, (response, hasError)->{
			System.out.println(response);
	        System.out.println(hasError);
	        response.get("item").getAsJsonObject().get("count").getAsInt();
	        });
	}
	
	@Test
	public void databaseGetItemCount2Test() {
		 client.databaseGetItemCount(test_partition, count_field, count_value, (response, hasError)->{
			System.out.println(response);
	        System.out.println(hasError);
	        response.get("item").getAsJsonObject().get("count").getAsInt();
	        });
	}
	
	@Test
	public void databaseGetItems1Test() {
		 client.databaseGetItems(test_partition, start_key, limit, (response, hasError)->{
			System.out.println(response);
	        System.out.println(hasError);
	        assertTrue(response.get("items").getAsJsonArray().isJsonArray());
	        });
	}
	
	@Test
	public void databaseGetItems2Test() {
		 client.databaseGetItems(test_partition, limit, (response, hasError)->{
			System.out.println(response);
	        System.out.println(hasError);
	        assertTrue(response.get("items").getAsJsonArray().isJsonArray());
	        });
	}
	
	@Test
	public void databasePutItemFieldTest() {
		 client.databasePutItemField(item_id, put_field, put_value, (response, hasError)->{
			System.out.println(response);
	        System.out.println(hasError);
	        assertNotNull(response.get("success"));
	        });
	}
	
	@Test
	public void databaseUpdateItem1Test() {
		 client.databaseUpdateItem(item_id, test_item_new, readGroups, writeGroups, (response, hasError)->{
			System.out.println(response);
	        System.out.println(hasError);
	        assertNotNull(response.get("success"));
	        });
	}

	@Test
	public void databaseUpdateItem2Test() {
		 client.databaseUpdateItem(item_id, test_item_new, readGroups, writeGroups, (response, hasError)->{
			System.out.println(response);
	        System.out.println(hasError);
	        assertNotNull(response.get("success"));
	        });
	}
	
	@Test
	public void databaseQueryItems1Test() {
		 client.databaseQueryItems(test_partition, query, start_key, limit, reverse, (response, hasError)->{
			System.out.println(response);
	        System.out.println(hasError);
	        assertTrue(response.get("items").getAsJsonArray().isJsonArray());
	        });
	}
	

	@Test
	public void databaseQueryItems2Test() {
		 client.databaseQueryItems(test_partition, query, (response, hasError)->{
			System.out.println(response);
	        System.out.println(hasError);
	        assertTrue(response.get("items").getAsJsonArray().isJsonArray());
	        });
	}
}
