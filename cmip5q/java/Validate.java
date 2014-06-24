import java.io.*;
import javax.xml.transform.Source;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.*;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

public class Validate {

    public static void main(String[] args) throws SAXException, IOException {

        // 1. Lookup a factory for the W3C XML Schema language
        SchemaFactory factory = 
            SchemaFactory.newInstance("http://www.w3.org/2001/XMLSchema");
        
        // 2. Compile the schema. 
        // Here the schema is loaded from a java.io.File, but you could use 
        // a java.net.URL or a javax.xml.transform.Source instead.
        Schema schema = null;
        try {
          File schemaLocation = new File(args[0]);
          schema = factory.newSchema(schemaLocation);
	}
        catch (Exception ex) {
            System.out.println(args[0] + " schema is not valid because ");
            System.out.println(ex.getMessage());
        }
        // 3. Get a validator from the schema.
        Validator validator = schema.newValidator();
        
        // 4. Parse the document you want to check.
        Source source = new StreamSource(args[1]);
        
        // 5. Check the document
        try {
            validator.validate(source);
            System.out.println(args[1] + " is valid.");
        }
        catch (SAXParseException ex) {
            System.out.println(args[1] + " is not valid because ");
            System.out.println(ex.getMessage());
	    System.out.println("   Line number: "+ex.getLineNumber());
	    System.out.println("   Column number: "+ex.getColumnNumber());
       }  
        
    }

}
