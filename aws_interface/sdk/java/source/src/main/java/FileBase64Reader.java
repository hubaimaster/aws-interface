import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Iterator;


public class FileBase64Reader implements Iterator<String> {

    private FileInputStream fileInputStream = null;
    private boolean hasNext = true;
    private int bufferSize = 1024 * 1024 * 3;

    FileBase64Reader(File file, int bufferSize){
        try {
            setInputStream(file, bufferSize);
        }catch (FileNotFoundException ex){
            this.hasNext = false;
        }
    }

    private void setInputStream(File file, int bufferSize) throws FileNotFoundException {
        this.fileInputStream = new FileInputStream(file);
        this.bufferSize = bufferSize;
    }

    private String toBase64String(byte[] bytes){
        byte[] encoded = Base64.getEncoder().encode(bytes);
        return new String(encoded, StandardCharsets.US_ASCII);
    }

    @Override
    public boolean hasNext() {
        return this.hasNext;
    }

    @Override
    public String next() {
        byte[] buffer = new byte[this.bufferSize];
        int readSize = 0;
        try {
            if ((readSize = this.fileInputStream.read(buffer)) != -1){
                String base64StringChunk = this.toBase64String(buffer);
                if (readSize < bufferSize){
                    this.hasNext = false;
                }
                return base64StringChunk;
            }else{
                this.hasNext = false;
                this.fileInputStream.close();
            }
        }catch (IOException ex){
            this.hasNext = false;
            return null;
        }
        return null;
    }

}
