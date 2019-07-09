import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class StorageTest {
	static AWSInterface client = new AWSInterface("https://e3t7xfb981.execute-api.ap-northeast-2.amazonaws.com/prod_aws_interface/ipxsNKvdpXUgzAMqg2JgdM");
	static String test_email = new String("ttest@gmail.com");
	static String test_password = new String("ttestpassword");
	static ArrayList<String> read_groups = new ArrayList<>();
	static ArrayList<String> write_groups = new ArrayList<>();
	
	static String file_dir = System.getProperty("user.dir");
	static String file_path = Paths.get(file_dir, "test.txt").toString();
	static String file_id = new String("ehCp8MVZXvoQLrZbUHcdwJ");
	static File file;
	
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
	
	static public void storageDeleteB64Test() {
		client.storageDeleteB64(file_id,(response, hasError)->{
            System.out.println(response);
            assertNotNull(response.get("success"));
        });
	}

    static public void storageDownloadB64Test(){
        client.storageDownloadB64(file_id,(response, hasError)->{
            System.out.println(response);
            assertNotNull(response.get("file_b64"));
        });
    }

    static public void storageDeleteFileTest(){
        client.storageDeleteFile(file_id,(response, hasError)->{
            System.out.println(response);
            assertNotNull(response.get("success"));
        });
    }

    static public void storageDownloadFileByteTest(){
        client.storageDownloadFileByte(file_id, (response, hasError)->{
            System.out.println(response);
            assertNotNull(response.get("file_b64"));
        }, filebyte -> {});
    }

    static public void storageUploadFileTest(){
        try {
        	client.storageUploadFile(file, read_groups, write_groups, (response, hasError)->{
        		file_id = response.get("file_id").toString();
        		assertNotNull(response.get("file_id"));
        		System.out.println(response);
        	});
    	}
        catch (Exception e){
        	e.printStackTrace();
        }
    }
	
	 public static void main(String[] args) {
		 writeFile();
		 read_groups.add("user");
		 write_groups.add("user");
		 client.authLogin(test_email, test_password, (response, hasError)->{
	            System.out.println(response);
	            //storageUploadFileTest();
	            storageDownloadFileByteTest();
	            //storageDeleteFileTest();
	            //storageUploadFileTest();
	            //storageDownloadB64Test();
	            //storageDeleteB64Test();
	        });
	 }
}


