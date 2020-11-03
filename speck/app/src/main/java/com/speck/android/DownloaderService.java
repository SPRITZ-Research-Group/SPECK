package com.speck.android;

import android.app.Service;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.os.AsyncTask;
import android.os.IBinder;
import android.content.Intent;
import android.preference.PreferenceManager;

import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
import android.util.Log;

//import com.speck.android.AppInfoActivity;
import com.speck.android.tools.FileReader;
import com.speck.android.tools.ServerCommunication;
import android.os.Messenger;
import android.os.Message;
import android.os.Bundle;
import android.os.RemoteException;
import android.app.PendingIntent;
import android.app.NotificationManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.os.Build;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.OutputStream;

public class DownloaderService extends Service {
    private SharedPreferences sharedPref;
    private Context context;
    private Messenger messageHandler;

    public static final String END_MSG = ".....END";

    /**
     LIFECYCLE
     **/

    @Override
    public int onStartCommand(Intent intent, int flags, int startId){
        super.onStartCommand(intent, flags, startId);
        //Toast.makeText(this, "Service Started", Toast.LENGTH_SHORT).show();
        this.context = this;
        sharedPref = PreferenceManager.getDefaultSharedPreferences(getBaseContext());

        Bundle extras = intent.getExtras();
        messageHandler = (Messenger) extras.get(ApplicationsFragment.MESSENGER);

        String request = intent.getStringExtra(ApplicationsFragment.SERVER_REQUEST);
        String position = intent.getStringExtra(ApplicationsFragment.REQUEST_ID);

        //sendForegroundNotification("Reaching server", request.split("&")[2].split("=")[1]);
        new DownloaderTask(request, position).executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);

        return START_STICKY;
    }

    @Override
    public void onDestroy(){
        //Toast.makeText(this, "Service destroyed", Toast.LENGTH_SHORT).show();
    }

    public void sendMessage(String msg) {
        Message message = Message.obtain();
        message.obj = msg;

        try {
            messageHandler.send(message);
        } catch (RemoteException e) {
            e.printStackTrace();
        }
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    /**
     NOTIFICATIONS
     **/

    public int getUniqueId(String filename){
        int uniqueId = 0;
        for (int i = 0; i < filename.length(); i++){
            uniqueId += Character.getNumericValue(filename.charAt(i));
        }
        return uniqueId;
    }

    public void closeNotification(String fileToFind){
        int uniqueCode = getUniqueId(fileToFind);
        NotificationManager mNotificationManager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        mNotificationManager.cancel(uniqueCode);
    }

    public void sendDownloadNotification(String msg, String appName, boolean show, String fileToFind){
        Intent notificationIntent = new Intent(this, MainActivity.class);

        int uniqueCode = getUniqueId(fileToFind);
        PendingIntent pendingIntent =
                PendingIntent.getActivity(this, 0, notificationIntent, PendingIntent.FLAG_CANCEL_CURRENT);

        NotificationCompat.Builder mBuilder =
                new NotificationCompat.Builder(this.getApplicationContext(), "notify_001");
        mBuilder.setContentIntent(pendingIntent);

        mBuilder.setSmallIcon(R.drawable.ic_notif);
        mBuilder.setContentTitle(msg);
        mBuilder.setPriority(Notification.PRIORITY_MAX);
        //mBuilder.setOnlyAlertOnce(true);
        mBuilder.setAutoCancel(false);
        mBuilder.setVisibility(Notification.VISIBILITY_PUBLIC);


        NotificationManager mNotificationManager =
                (NotificationManager) this.getSystemService(Context.NOTIFICATION_SERVICE);

        mNotificationManager.notify(uniqueCode, mBuilder.build());
    }

    public void sendEndNotification(String title, String msg, boolean withAnIntent, String fileToFind){
        // send notification only if the user is not on the main activity app
        if (MainActivity.isRunning == false) {
            NotificationCompat.Builder mBuilder =
                    new NotificationCompat.Builder(this.getApplicationContext(), "notify_001");

            int uniqueCode = getUniqueId(fileToFind);
            if (withAnIntent) {
                Intent ii = new Intent(this.getApplicationContext(), ReportActivity.class);
                ii.putExtra(ApplicationsFragment.SERVER_MESSAGE, fileToFind);
                PendingIntent pendingIntent = PendingIntent.getActivity(this, uniqueCode, ii, PendingIntent.FLAG_CANCEL_CURRENT);
                mBuilder.setContentIntent(pendingIntent);
            } else {
                Intent ii = new Intent(this.getApplicationContext(), MainActivity.class);
                PendingIntent pendingIntent = PendingIntent.getActivity(this, uniqueCode, ii, PendingIntent.FLAG_CANCEL_CURRENT);
                mBuilder.setContentIntent(pendingIntent);
            }

            mBuilder.setSmallIcon(R.drawable.ic_notif);

            mBuilder.setContentTitle(title);
            mBuilder.setContentText(msg);
            mBuilder.setPriority(Notification.PRIORITY_MAX);
            mBuilder.setAutoCancel(true);
            mBuilder.setVisibility(Notification.VISIBILITY_PUBLIC);

            NotificationManager mNotificationManager =
                    (NotificationManager) this.getSystemService(Context.NOTIFICATION_SERVICE);

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                NotificationChannel channel = new NotificationChannel("notify_001",
                        "An analysis is running...",
                        NotificationManager.IMPORTANCE_DEFAULT);
                mNotificationManager.createNotificationChannel(channel);
            }

            mNotificationManager.notify(uniqueCode, mBuilder.build());
        }
    }

    /**
     ASYNC TASK
     **/

    private String getApkDir(String pkg){
        String apkPath = "";
        try {
            ApplicationInfo app = getPackageManager().getApplicationInfo(pkg, 0);
            apkPath = app.sourceDir;
        } catch (PackageManager.NameNotFoundException e){
            Log.e("Exception found ", e.getMessage());
        }
        return apkPath;
    }

    private class DownloaderTask extends AsyncTask<Void, String, Void> {
        private String default_ip = getString(R.string.default_ip);
        private int default_port = Integer.parseInt(getString(R.string.default_port));

        private String server_request;
        private String server_reply = "";

        private ServerCommunication server = null;

        private String position;
        private String pkg;
        private String vers;
        private String appName;

        private DownloaderTask(String server_request, String position){
            super();
            this.server_request = server_request;
            this.position = position;
            this.pkg = server_request.split("&")[0].split("=")[1];
            this.vers = server_request.split("&")[1].split("=")[1];
            this.appName = server_request.split("&")[2].split("=")[1];
        }

        @Override
        protected Void doInBackground(Void... params) {
            // Get IP & PORT & OPTION
            String ip = sharedPref.getString("ip", default_ip);
            int port = Integer.parseInt(sharedPref.getString("port", String.valueOf(default_port)));
            boolean option = sharedPref.getBoolean("checkboxPref", false);
            sendDownloadNotification(this.pkg + " is being analysed...", this.appName, true, this.pkg + "_" + this.vers);
            try {
                server = new ServerCommunication(ip, port);
                ApplicationsFragment.socketList.set(Integer.parseInt(this.position), server);

                // Create socket
                server.init();
                if (server.errorOccurred()) { return null; }
                sendMessage("position="+this.position+"&status=Checking app availability&step=2");

                // Send message
                String withApk = "&withAPK=false";
                if (option){ withApk = "&withAPK=true"; }
                server.sendmsg(this.server_request + withApk);

                // OPTION: SEND APK TO THE SERVER
                if (option){
                    String apk = getApkDir(this.pkg);

                    try {
                        File f = new File(apk);
                        OutputStream os = server.getOs();
                        byte[] buffer = new byte[1024];
                        FileInputStream in = new FileInputStream(f);
                        BufferedInputStream bis = new BufferedInputStream(in);
                        int byteSize;
                        while((byteSize = bis.read(buffer, 0, 1024)) != -1) {
                            os.write(buffer, 0, byteSize);
                        }
                        os.flush();

                    } catch (IOException e) {
                        Log.e("APK OPTION exception", e.getMessage());
                        e.printStackTrace();
                    }
                }

                server.sendmsg(END_MSG);

                // Get messages
                this.server_reply = server.getmsg();
                while (!this.server_reply.split("=")[0].equals("packageName") && !server.errorOccurred()){
                    if (this.server_reply.split("=")[0].equals("status")){
                        sendMessage("position="+this.position+"&"+this.server_reply);
                        //sendForegroundNotification(this.server_reply.split("&")[0].split("=")[1], this.appName);
                    } else if (this.server_reply.split("#")[0].equals("manifest")){
                        // Save manifest in a file
                        FileReader fileReader = new FileReader(context, "manifest_" + this.pkg + "_" + this.vers + ".xml");
                        fileReader.write(this.server_reply.split("#")[1]);
                    }

                    this.server_reply = server.getmsg();
                }

                // Close Server Socket
                server.close();
            } catch(RuntimeException e){
                Log.e("doInBackgr exception", Log.getStackTraceString(e));
                server.setError("Unable to reach the server.");
            }

            return null;
        }

        @Override
        protected void onPostExecute(Void result) {
            super.onPostExecute(result);

            closeNotification(this.pkg + "_" + this.vers);
            if (server.errorOccurred()){
                sendMessage("position="+this.position+"&"+"error="+server.getError()+"&filename="+this.pkg + "_" + this.vers);
                sendEndNotification("An error occurred with " + this.pkg, server.getError(), false, this.pkg + "_" + this.vers);
            } else {
                // Save data in a file
                FileReader fileReader = new FileReader(context, this.pkg + "_" + this.vers);
                fileReader.write(this.server_reply);
                sendMessage("position="+this.position+"&"+this.server_reply);
                sendEndNotification("Analysis completed!", this.pkg + " has been analysed.", true, this.pkg + "_" + this.vers);
            }
            stopSelf();

        }

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
        }
    }
}


