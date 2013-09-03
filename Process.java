import java.io.*;
import java.net.*;


class Process{


	Socket clientSocket;
	PrintWriter out;
	BufferedReader in;


	Process(){

	


	}



	public void start(String[] argv){


		if(argv.length < 1){
			System.err.println("No text in parameter");
			System.exit(1);
		}
		
		openSockets();

		try {

			out.println(argv[0]);

			System.out.println(in.readLine());


		} catch (IOException e ){
			e.printStackTrace();
		}

	}



	public void openSockets(){


                try{
                        clientSocket = new Socket("localhost", 8087);

                        out = new PrintWriter(clientSocket.getOutputStream(), true);
                        in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));


                } catch (IOException e) {
                        e.printStackTrace();
		}


	}






	public static void main(String[] argv){


		new Process().start(argv);

	}



}
