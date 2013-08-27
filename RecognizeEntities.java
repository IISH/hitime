import java.sql.*;

import java.io.*;
import java.net.*;

class RecognizeEntities {


	boolean DEBUG = true;
			

	Connection con = null;
//	String DATABASE_URL = "jdbc:mysql://195.169.123.195:10000/bwsa";
        String DATABASE_URL = "jdbc:mysql://localhost:3306/test";

        String DATABASE_USER = "bwsa";
        String DATABASE_PASSWORD = "bwsa";

	public String argument = "";
	int NER_STANDARD_PORT = 8085;
	int NER_TILBURG_PORT = 8086;

        public final static String TIMERANGE = "timerange";
        public final static String NUMBER = "NUMBER";
        public final static String WORD = "WORD";
        public final static String UNKNOWN = "UNKNOWN BY UCTO";
	public final static String PUNCT= "PUNCT";


	Socket standardSocket;
	Socket tilburgSocket;
	DataInputStream dInStandard;
	DataOutputStream dOutStandard;

	DataInputStream dInTilburg;
	DataOutputStream dOutTilburg;

	OutputStream outStandard;
	OutputStream outTilburg;

	int nrUnprocessedDocs;

	public RecognizeEntities(){
		nrUnprocessedDocs = 0;	
                // open database connection:
		openDbConnection();

	}


	public void openDbConnection(){

                try {
                        Class.forName("com.mysql.jdbc.Driver");
                } catch (ClassNotFoundException e) {
                        throw new RuntimeException("Cannot find the driver in the classpath!", e);
                }


                try {

                        con = DriverManager.getConnection(DATABASE_URL, DATABASE_USER, DATABASE_PASSWORD);
                } catch (SQLException ex) {

                        ex.printStackTrace();
			System.exit(1);

                } 


	}



	public void start(){
		try {
	
			makeSpans();

		} catch (SQLException e) {

			e.printStackTrace();

		}

	}




	public void makeSpans() throws SQLException {
                String processedDocument = "";
		String word = "";
		String ner = "";

		// get raw text:
                Statement st1 = con.createStatement();
                String query = "SELECT raw FROM test WHERE id=1;";
                ResultSet rawDocResult = st1.executeQuery(query);
                rawDocResult.next();
                String rawDocument = rawDocResult.getString("raw");

		query = "SELECT * FROM coordinates JOIN tokens ON tokens.word_id = coordinates.word_id LEFT JOIN meanings ON meanings.id = coordinates.id ORDER BY coordinates.id ASC;"; 
                Statement st = con.createStatement();
                ResultSet wordsAndMeanings = st.executeQuery(query);



		while(wordsAndMeanings.next()){
			word = wordsAndMeanings.getString("word");
			ner = wordsAndMeanings.getString("ner");

                        
			// remove space before punctuation:
			if(word.matches("'.|[\\?\\.\\,\\;\\!¡¿。、·]")){
                                processedDocument = processedDocument.substring(0, processedDocument.length()-1);
                        }


			if(ner != null){
				processedDocument += createTag(ner);
			}

			processedDocument += word;


			// idee: als ner.equals("PERS-B") geen </span>
			if(ner != null){
				processedDocument += "</span>";
			}

			processedDocument += " ";
			
		}

                PreparedStatement st3 = con.prepareStatement("UPDATE test SET highlighted=? WHERE id=1;");

                st3.setString(1, processedDocument);

                int rs = st3.executeUpdate();


	}

	public String createTag(String ner){
		if (ner.equals("PERSON")){

			return "<span class='person_stanford'>";

		} else if (ner.equals("ORGANISATION")){

			return "<span class='organisation_stanford'>";

		}else if (ner.equals("DATE")){

			return "<span class='date_stanford'>";

                }else if (ner.equals("LOCATION")){

			return "<span class='location_stanford'>";

                }else if (ner.equals("MISC")){

			return "<span class='misc_stanford'>";

                } else {

			return "<span class='unknown_tag_stanford'>";

		}
	}



	public static void main(String[] argv){


		new RecognizeEntities().start();

	}
}
