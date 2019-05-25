


public class Examples {
    public static void main(String[] args) {
        AWSInterface client = new AWSInterface("{{REST_API_URL}}");
        client.authLogin("example@email.com", "pass1234", (response, hasError)->{
            System.out.println(response);
        });
    }
}

