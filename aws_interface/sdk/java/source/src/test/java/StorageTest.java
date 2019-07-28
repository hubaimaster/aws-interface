import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertEquals;
import java.util.concurrent.Callable;
import static org.awaitility.Awaitility.*;
import static java.util.concurrent.TimeUnit.SECONDS;

public class StorageTest {
	AWSInterface client = new AWSInterface("https://e3t7xfb981.execute-api.ap-northeast-2.amazonaws.com/prod_aws_interface/ipxsNKvdpXUgzAMqg2JgdM");
	String test_email = new String("ttest@gmail.com");
	String test_password = new String("ttestpassword");
	static ArrayList<String> readGroups = new ArrayList<>();
	static ArrayList<String> writeGroups = new ArrayList<>();
	
	static String file_dir = System.getProperty("user.dir");
	static String file_path = Paths.get(file_dir, "test.txt").toString();
	static String file_id ="G9vDDvTz8AT54TS4qwsXKJ";
	static File file;
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
	
	@BeforeAll
	static public void writeFile() {
		try {
			file = new File(file_path);
			FileWriter fw = new FileWriter(file, false);
			fw.write("this is test text");
			fw.flush();
			fw.close();
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}

	@BeforeAll
	static public void setValues() {
		 readGroups.add("user");
		 writeGroups.add("user");

	}
	// Before each testcase, initialize received flag with false to use awaitility for async testing
	@BeforeEach
	public void initialiize() {
		received = false;
		received2 = false;
	}

	@Test
    public void storageTest(){
    	client.authLogin(test_email, test_password,(rr, hE)->{
		try {
			//UploadFile with [readGroups], [writeGroups] and save file_id to [file_id]
	        	client.storageUploadFile(file, (response, hasError)->{
	        		file_id = response.get("file_id").getAsString();
	        		assertNotNull(response.get("file_id").getAsString());
	        		System.out.println("upload "+ response);
	    	        received2 = true;
            });
      }
		catch (Exception e){
			e.printStackTrace();
        }
	});
    	//Wait for the upload to finish at most 20 seconds
    	await().atMost(20, SECONDS).until(responseReceived2());
    	received2 = false;

    	//Download file with file_id
    	client.storageDownloadFileByte(file_id, (response, hasError)->{
            System.out.println("download "+response);
            //assertTrue(response.get("success").getAsBoolean());
            received2 = true;
        }, (filebyte)->{});
    	//Wait for the download to finish at most 20 seconds
    	await().atMost(20, SECONDS).until(responseReceived2());
    	
    	//Delet the file with file_id
    	client.storageDeleteFile(file_id,(response, hasError)->{
            System.out.println("delete "+response);
            //assertTrue(response.get("success").getAsBoolean());
            received = true;
        });
    	//Wait for all the processes at most 30 seconds
        await().atMost(30, SECONDS).until(responseReceived());
    }
}


