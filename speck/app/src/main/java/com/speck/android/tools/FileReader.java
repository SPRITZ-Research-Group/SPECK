package com.speck.android.tools;

import java.io.FileOutputStream;
import java.io.FileInputStream;
import java.io.File;

import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;

import androidx.core.app.ActivityCompat;
import android.util.Log;

import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.util.List;

public class FileReader {
    private String filename;
    private FileOutputStream outputStream;
    private FileInputStream inputStream;
    private Context context;

    public FileReader(Context context, String filename){
        this.context = context;
        this.filename = filename;
    }

    public FileReader(Context context){
        this.context = context;
    }

    public String getFilename(int position, List<ApplicationInfo> applist){
        ApplicationInfo data = applist.get(position);
        String pkg = data.packageName;
        String versionName = "";

        try {
            versionName = context.getPackageManager().getPackageInfo(data.packageName, 0).versionName;
        } catch(PackageManager.NameNotFoundException e) {
            Log.e("Exception found ", e.getMessage());
        }

        return pkg + '-' + versionName;
    }

    public boolean fileExists(String name){
        File file = this.context.getFileStreamPath(name);
        return file.exists();
    }

    public void deleteFile(String name){
        File dir = this.context.getFilesDir();
        File file = new File(dir, name);
        file.delete();
    }

    public void write(String content){
        try {
            outputStream = this.context.openFileOutput(this.filename, Context.MODE_PRIVATE);
            outputStream.write(content.getBytes());
            outputStream.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public String read(){
        String s = new String();
        try {
            inputStream = this.context.openFileInput(this.filename);
            InputStreamReader isr = new InputStreamReader(inputStream);
            BufferedReader bufferedReader = new BufferedReader(isr);
            String line;
            while ((line = bufferedReader.readLine()) != null) {
                s += line;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return s;
    }

}
