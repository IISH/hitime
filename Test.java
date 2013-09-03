import edu.stanford.nlp.trees.semgraph.SemanticGraphCoreAnnotations.CollapsedCCProcessedDependenciesAnnotation;
import edu.stanford.nlp.dcoref.CorefCoreAnnotations.CorefChainAnnotation;
import edu.stanford.nlp.dcoref.CorefCoreAnnotations.CorefGraphAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.NamedEntityTagAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.PartOfSpeechAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TextAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.trees.TreeCoreAnnotations.TreeAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.dcoref.CorefChain;
import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.semgraph.SemanticGraph;
import edu.stanford.nlp.util.CoreMap;
import edu.stanford.nlp.util.IntTuple;
import edu.stanford.nlp.util.Pair;
import edu.stanford.nlp.util.Timing;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.PreparedStatement;
import java.util.*;
import java.lang.*;
import java.util.regex.*;
import java.util.Properties;
import java.io.*;
import java.net.*;

class Test{

	public final static int LINE = 6;
	public final static int WORD_START = 8;
	public final static int WORD_END = 10; 
	public final static int EG_ID = 4;
	public final static int EG_ENTITY = 2;

        public final static String MYSQL_HOST = "jdbc:mysql://localhost:3306/";
	StanfordCoreNLP pipeline;
	Properties props;
	ServerSocket serverSocket;
	PrintWriter out;
	BufferedReader in;
	
	Connection con;	
	Socket connection;

	Test(){
		
		openDbConnection();

		props = new Properties();
                props.put("annotators", "tokenize, ssplit,parse,lemma, ner");
                pipeline = new StanfordCoreNLP(props);
			

	}

	public void start(){

		String message = "";

		try{
			serverSocket = new ServerSocket(8087);
			System.out.println("Waiting for connection");
			connection = serverSocket.accept();
			System.out.println("Connection received from " + connection.getInetAddress().getHostName());

			out = new PrintWriter(connection.getOutputStream(), true);

			in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
 
			
			do {

				try {
					message = in.readLine();
					if(message == null) break;
					System.out.println(">" + message + "<");


					// tokenize text with NLP and insert in DB:
					processNLP(message);	

					// parse Evergreen output and insert in DB:
					//processEvergreen();


					out.println("DONE");
				} catch (IOException e) {
					e.printStackTrace();
				} catch (SQLException e){
					e.printStackTrace();
				}

			} while (!message.equals(""));
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			try {
				in.close();
				out.close();
				serverSocket.close();
			} catch (IOException e){
				e.printStackTrace();
			}
		}	


	}


	public void processNLP(String text) throws SQLException {


		// create an empty Annotation just with the given text
		Annotation document = new Annotation(text);

		// run all Annotators on this text
		pipeline.annotate(document);

		// these are all the sentences in this document
		// a CoreMap is essentially a Map that uses class objects as keys and has values with custom types
		List<CoreMap> sentences = document.get(SentencesAnnotation.class);

		insertInDB(sentences);



	}

	public void insertInDB(List<CoreMap> sentences) throws SQLException {

                HashMap hashMap = new HashMap();
		//String tokenQuery = "INSERT INTO tokens (filestem, word_id, word) VALUES ";
		//String coordinateQuery = "INSERT INTO coordinates (id, doc_id, sentence_id, position, word_id, meaning_flag) VALUES ";
		//String meaningQuery = "INSERT IGNORE INTO meanings (id,ner,ner_tilburg,frog,heideltime,ucto,evergreen,decision) VALUES ";
		int linenr = 0;
		int wordnr = 0;
		int wordId = 0;
		int id = 0;

		PreparedStatement tokenStatement = con.prepareStatement("INSERT INTO tokens (filestem, word_id, word) VALUES (?, ?, ?)");
		PreparedStatement coordinateStatement = con.prepareStatement("INSERT INTO coordinates (id, doc_id, sentence_id, position, word_id, meaning_flag) VALUES (?, ?, ?, ? ,? ,?)");
		PreparedStatement meaningStatement = con.prepareStatement("INSERT IGNORE INTO meanings (id,ner) VALUES (?, ?)");
	

		for(CoreMap sentence: sentences) {
			// traversing the words in the current sentence
			// a CoreLabel is a CoreMap with additional token-specific methods
			for (CoreLabel token: sentence.get(TokensAnnotation.class)) {
				// this is the text of the token
				String word = token.get(TextAnnotation.class);

				// this is the NER label of the token
				String ne = token.get(NamedEntityTagAnnotation.class);

				coordinateStatement.setInt(1, id);
				coordinateStatement.setString(2, "1");
				coordinateStatement.setInt(3, linenr);
				coordinateStatement.setInt(4, wordnr);

				if(!ne.equals("O")){
					//meaningQuery += "(" + id + ",'" + ne + "','','','','','',''),";
					meaningStatement.setInt(1, id);
					meaningStatement.setString(2,ne);
					meaningStatement.addBatch();
					coordinateStatement.setInt(6, 1);

				} else {
					coordinateStatement.setInt(6, 0);
				}

				if(hashMap.get(word) == null){

					//tokenQuery += "('1'," + wordId + ",'" + word + "'),";
					tokenStatement.setString(1, "1");
					tokenStatement.setInt(2, wordId);
					tokenStatement.setString(3, word);
					tokenStatement.addBatch();
					//coordinateQuery += "(" + id + ",'1'," + linenr + "," + wordnr + "," + wordId + ", 0),";					
					coordinateStatement.setInt(5, wordId);
					hashMap.put(word,wordId);
					wordId++;

				} else {

					int hashId = (Integer)hashMap.get(word);
					//coordinateQuery += "(" + id + ",'1'," + linenr  + "," + wordnr + "," + hashId + ",0),";
                                        coordinateStatement.setInt(5, hashId);

				}
				coordinateStatement.addBatch();

				id++;
				wordnr++;

			}

			linenr++;
			wordnr = 0;
		}

		System.out.println("Putting tokens in database");
		tokenStatement.executeBatch();
		coordinateStatement.executeBatch();
		meaningStatement.executeBatch();
		con.commit();
		System.out.println("done");

	}



	public void processEvergreen() throws SQLException {

                String query = "SELECT evergreenoutput FROM test WHERE id=1;";
                Statement st = con.createStatement();
                ResultSet rs = st.executeQuery(query);
		String egOutput;
		

		if(!rs.next()){ 
			return;
		}


		egOutput = rs.getString("evergreenoutput");
		String[] egOutputLines = egOutput.split("<br>");

		String upsertQuery = "INSERT INTO meanings (id, evergreen, evergreen_id) ";

		for(String egOutputLine : egOutputLines) {
			
			String[] tokens = egOutputLine.split(";");
			int line = Integer.parseInt(tokens[LINE]);
			int wordStart = Integer.parseInt(tokens[WORD_START]);
			int wordEnd = Integer.parseInt(tokens[WORD_END]);
			int egId = Integer.parseInt(tokens[EG_ID]);
			String egEntity = tokens[EG_ENTITY];


			if(wordStart == wordEnd) { // Single entity

				upsertQuery = "INSERT INTO meanings (id, evergreen, evergreen_id) SELECT id, '" + egEntity + "'," + egId 
					      + " FROM coordinates WHERE sentence_id= " + line 
					      + " AND position=" + wordStart + " ON DUPLICATE KEY UPDATE evergreen_id=VALUES(evergreen_id), evergreen=VALUES(evergreen) ; ";
			

			} else {   // multi-word entity

				// ASSUMPTION: Multiple words do not span multiple sentences.

				upsertQuery = "INSERT INTO meanings (id, evergreen, evergreen_id) SELECT id, '" + egEntity + "'," + egId 
				+ " FROM coordinates WHERE sentence_id=" + line 
                                + " AND position BETWEEN " + wordStart + " AND " + wordEnd + " ON DUPLICATE KEY UPDATE evergreen_id=VALUES(evergreen_id), evergreen=VALUES(evergreen) ; ";


			}


/*

INSERT INTO meanings (id, evergreen, evergreen_id) 
(SELECT id,  'Marx, Karl', 153540
FROM coordinates
WHERE sentence_id =0
AND position
BETWEEN 8 
AND 9 
OR sentence_id =3
AND position=13
) 
ON DUPLICATE KEY UPDATE evergreen_id=VALUES(evergreen_id), evergreen=VALUES(evergreen) ;
*/


		

			System.out.println(upsertQuery);
		}

	}



	public static void main (String[] args) {

		Test test = new Test();
		while(true){

			test.start();
		}

	}




	// DATABASE OPERATIONS
        public void openDbConnection(){

                try {
                        Class.forName("com.mysql.jdbc.Driver");
                } catch (ClassNotFoundException e) {
                        throw new RuntimeException("Cannot find the driver in the classpath!", e);
                }


                try {

                        con = DriverManager.getConnection(MYSQL_HOST + "test" , "bwsa", "bwsa");
			con.setAutoCommit(false);
                } catch (SQLException ex) {

                        ex.printStackTrace();
                        System.exit(1);

                }


        }




        public void runInsertQuery(String query) {


                Statement st = null;
                int rs = 0;


                try {

                        st = con.createStatement();

                        rs = st.executeUpdate(query);

                } catch (SQLException ex) {

                        ex.printStackTrace();

                } 


        }



}
