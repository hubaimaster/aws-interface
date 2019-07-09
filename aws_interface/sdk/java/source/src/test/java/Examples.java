import static org.junit.jupiter.api.Assertions.assertNotNull;

import java.util.ArrayList;
import java.util.HashMap;
public class Examples {
	static AWSInterface client = new AWSInterface("https://e3t7xfb981.execute-api.ap-northeast-2.amazonaws.com/prod_aws_interface/ipxsNKvdpXUgzAMqg2JgdM");
    	
    public static void main(String[] args) {
    	
        client.authLogin("ttest@gmail.com", "ttestpassword", (response, hasError)->{
            System.out.println(response);
            client.authLogout((rr, hE)->{
                System.out.println(rr);
            });
        });

    }
}