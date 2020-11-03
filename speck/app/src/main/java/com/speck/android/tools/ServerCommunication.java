package com.speck.android.tools;

import java.io.OutputStream;
import java.io.PrintWriter;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.net.Socket;
import java.net.UnknownHostException;
import java.net.SocketAddress;
import java.net.InetSocketAddress;

import android.util.Log;

import com.speck.android.DownloaderService;

public class ServerCommunication{
    private String server_ip ;
    private int server_port;

    private Socket socket = null;
    private PrintWriter out = null;
    private BufferedReader in = null;

    private OutputStream os = null;

    private String error_msg = "";

    public ServerCommunication(String ip, int port){
        this.server_ip = ip;
        this.server_port = port;
    }

    public void init(){
        if (isReachable()) {
            try {
                this.socket = new Socket(this.server_ip, this.server_port);
                this.os = socket.getOutputStream();
                this.out = new PrintWriter(os, true);
                this.in = new BufferedReader(new InputStreamReader(socket.getInputStream()));

            } catch (UnknownHostException e) {
                this.error_msg = "Unknown host.";
                Log.e("Server init ", e.getMessage());
            } catch (IOException e) {
                this.error_msg = "Socket exception.";
                Log.e("Server init ", e.getMessage());
            }
        }
    }

    private boolean isReachable(){
        boolean exists = false;

        try {
            SocketAddress sockaddr = new InetSocketAddress(this.server_ip, this.server_port);
            // Create an unbound socket
            Socket sock = new Socket();

            // If the timeout occurs, SocketTimeoutException is thrown.
            int timeoutMs = 2000;   // 2 seconds
            sock.connect(sockaddr, timeoutMs);
            exists = true;

            // Send 'end' data
            OutputStream osLocal = sock.getOutputStream();
            PrintWriter outLocal = new PrintWriter(osLocal, true);
            outLocal.println(DownloaderService.END_MSG);
            osLocal.close();

        } catch(IOException e) {
            this.error_msg = "Server not reachable. Please check your internet connection or try again later.";
            Log.e("Server Reach ",e.getMessage());
        }
        return exists;
    }

    public String getmsg(){
        String reply = "";

        try{
            reply = this.in.readLine();
        } catch (IOException e) {
            this.error_msg = "Unable to reach the server.";
            Log.e("Server Get ",e.getMessage());
        }

        if (reply.equals("")){
            this.error_msg = "No reply from the server.";
        } else if (reply.split("=")[0].equals("error")){
            this.error_msg = reply.split("=")[1];
        }

        return reply;
    }

    public void sendmsg(String msg){
        this.out.println(msg);
    }

    public void close(){
        try{
            if (this.socket != null) {
                this.socket.close();
            }
        } catch (IOException e) {
            this.error_msg = "Error while closing socket.";
            Log.e("Server Send ",e.getMessage());
        }
    }

    public boolean errorOccurred(){
        return !this.error_msg.equals("");
    }

    public String getError(){
        return this.error_msg;
    }

    public void setError(String msg) { this.error_msg = msg; }

    public Socket getSocket(){
        return this.socket;
    }

    public OutputStream getOs() {
        return os;
    }
}
