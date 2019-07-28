import org.junit.jupiter.api.*;
import java.util.concurrent.Callable;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.HashMap;
import static java.util.concurrent.TimeUnit.SECONDS;
import static org.awaitility.Awaitility.*;

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
	String item_id = "UEyUXQ4XLs53nV9xPz3tdD";
	String start_key = "0";
	int limit = 10;
	boolean reverse = false;
	boolean received = false;
	boolean received2 = false;
	
	//Declare Callable object for check if the response is received;
	private Callable<Boolean> responseReceived(){
		return new Callable<Boolean>() {
			public Boolean call() throws Exception{
				return received;
			}
		};
	}
	
	//Declare Callable object for check if the response is received;
	private Callable<Boolean> responseReceived2(){
		return new Callable<Boolean>() {
			public Boolean call() throws Exception{
				return received2;
			}
		};
	}

	// Before each testcase, initialize received flag with false to use awaitility for async testing
	@BeforeEach
	public void initialiize() {
		received = false;
		received2 = false;
	}
	
	@BeforeAll
	public static void setValues() {
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
	}

	//Create item, get item with [item_id], delete item
	@Test
	public void databaseCreateGetDeleteItemTest() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.databaseCreateItem(test_partition, test_item, (response, hasError)->{
				item_id = response.get("item_id").getAsString();
				received2 = true;
			});
			// Wait until item is created
			await().until(responseReceived2());
			received2 = false;
			
			client.databaseGetItem(item_id, (response, hasError)->{
				assertNotNull(response.get("item").getAsJsonObject());
				received2 = true;
			});
			// wait before deleting item.
			await().until(responseReceived2());
			
			client.databaseDeleteItem(item_id, (response, hasError)->{
				assertNotNull(response.get("success").getAsString());
				received = true;
			});					
		});
		//wait until responseReceived turns into true;
		await().atMost(30,SECONDS).until(responseReceived());
	}

	//Test create item with [readGroups], [writeGroups], [test_item] on [test_partition]
	@Test
	public void databaseCreateItem2Test() {
		client.authLogin(test_email, test_password, (rr, hE)-> {
			client.databaseCreateItem(test_partition, test_item, (response, hasError)->{
				assertNotNull(response.get("item_id"));
	         	received = true;
         	});
		});
		await().until(responseReceived());
	}

	//Test getting item count of [test_partition]
	@Test
	public void databaseGetItemCount1Test() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.databaseGetItemCount(test_partition, (response, hasError)->{
				response.get("item").getAsJsonObject().get("count").getAsInt();
		        received = true;
	        });
		});
		//wait until responseReceived turns into true;
		await().until(responseReceived());
	}
	
	// Test getting item count of [test_partition] which has [count_value] in [count_field]
	@Test
	public void databaseGetItemCount2Test() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.databaseGetItemCount(test_partition, count_field, count_value, (response, hasError)->{
				response.get("item").getAsJsonObject().get("count").getAsInt();
				received = true;
			});
		});
		//wait until responseReceived turns into true;
		await().until(responseReceived());
	}
	
	// Test Getting items with [start_key] and [limit] of [test_partition]
	@Test
	public void databaseGetItems1Test() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.databaseGetItems(test_partition, start_key, limit, (response, hasError)->{
				assertTrue(response.get("items").getAsJsonArray().isJsonArray());
			    received = true;
		    });
		});
		//wait until responseReceived turns into true;
		await().until(responseReceived());
	}
	
	// Test Getting items with [limit] but without [start_key] of [test_partition]
	@Test
	public void databaseGetItems2Test() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.databaseGetItems(test_partition, limit, (response, hasError)->{
				assertTrue(response.get("items").getAsJsonArray().isJsonArray());
			    received = true;
		    });
		});
		//wait until responseReceived turns into true;
		await().until(responseReceived());
	}

	
	//Test Putting [put_field] with [put_value] on item with [item_id]
	@Test
	public void databasePutItemFieldTest() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.databaseCreateItem(test_partition, test_item, (response1, hasError1)->{
				item_id = response1.get("item_id").getAsString();
				client.databasePutItemField(item_id, put_field, put_value, (response, hasError)->{
					assertNotNull(response.get("success"));
					received2 = true;
				});
			});
			// Wait until item is created
			await().until(responseReceived2());
			// Delete the item.
			client.databaseDeleteItem(item_id, (response1, hasError1)-> {
				received = true;
			});
		});	
		//Wait until responseReceived turns into true;
		await().until(responseReceived());
	}
	
	
	//Test Updating item with [item_id] to [test_item_new], [readGroups], [writeGroups]
	@Test
	public void databaseUpdateItem1Test() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.databaseCreateItem(test_partition, test_item, (response1, hasError1)->{
				item_id = response1.get("item_id").getAsString();
				client.databaseUpdateItem(item_id, test_item_new, (response, hasError)->{
					assertNotNull(response.get("success"));
			        received2 = true;
				});
			});
			// Wait until item is created
			await().until(responseReceived2());
			// Delete the item.
			client.databaseDeleteItem(item_id, (response1, hasError1)-> {
				received = true;
			});
		});
		//Wait until responseReceived turns into true;
		await().until(responseReceived());
	}

	// Test updating item with [item_id] to [test_item_new]
	@Test
	public void databaseUpdateItem2Test() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.databaseCreateItem(test_partition, test_item, (response1, hasError1)->{
				item_id = response1.get("item_id").getAsString();
				client.databaseUpdateItem(item_id, test_item_new, (response, hasError)->{
					assertNotNull(response.get("success"));
					received2 = true;
				});
			});
			// Wait until item is created
			await().until(responseReceived2());
			// Delete the item.
			client.databaseDeleteItem(item_id, (response1, hasError1)-> {
				received = true;
			});
		});
		//Wait until responseReceived turns into true;
		await().until(responseReceived());
	}
	
	//Test querying [query] on partition [test_partition] and retrieving the object from [start_key] with [limit].
	//Query is a list of hashmap
	@Test
	public void databaseQueryItems1Test() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.databaseQueryItems(test_partition, query, start_key, limit, reverse, (response, hasError)->{
				assertTrue(response.get("items").getAsJsonArray().isJsonArray());
		        received = true;
			});
		});
		//Wait until responseReceived turns into true;
		await().until(responseReceived());
	}
	
	//Test querying [query] on partition [test_partition] and retrieving the object with [limit].
	//Query is a list of hashmap
	@Test
	public void databaseQueryItems2Test() {
		client.authLogin(test_email, test_password, (rr, hE)->{
			client.databaseQueryItems(test_partition, query, (response, hasError)->{
				assertTrue(response.get("items").getAsJsonArray().isJsonArray());
		        received = true;
			});
		});
		//Wait until responseReceived turns into true;
		await().until(responseReceived());
	}
}
