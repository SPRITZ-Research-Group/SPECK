package com.speck.android.struct;

import android.graphics.drawable.Drawable;
import android.content.Context;
import android.util.Log;

import com.speck.android.tools.FileReader;

public class AppItem {
    private String appName;
    private String packageName;
    private String versionName;
    private Drawable appIcon;

    private boolean analysed;

    private boolean inProgress;
    private String progressTitle;
    private String progressLevel;

    private String fileNameToFind;
    private String manifest;

    public AppItem(Context context, String app, String pkg, String vers, Drawable icon){
        this.appName = app;
        this.packageName = pkg;
        this.versionName = vers;
        this.appIcon = icon;

        fileNameToFind = this.packageName + "_" + this.versionName;
        manifest = "manifest_" + this.packageName + "_" + this.versionName + ".xml";
        FileReader reader = new FileReader(context);

        if (reader.fileExists(fileNameToFind)) {
            this.analysed = true;
        } else{
            this.analysed = false;
        }

        this.inProgress = false;
        this.progressTitle = "";
        this.progressLevel = "";
    }

    public void setProgress(boolean b, String title, String text){
        this.inProgress = b;
        this.progressTitle = title;
        this.progressLevel = text;
    }

    public  String getFileNameToFind(){ return this.fileNameToFind; }

    public  String getManifest(){ return this.manifest; }

    public void setAnalyse(boolean b){
        this.analysed = b;
    }

    public String getVersion(){
        return this.versionName;
    }

    public String getPkg(){
        return this.packageName;
    }

    public String getFileName(){
        return this.packageName + "_" + this.versionName;
    }

    public String getAppName(){
        return this.appName;
    }

    public Drawable getAppIcon(){
        return this.appIcon;
    }

    public boolean wasAnalysed(){
        return this.analysed;
    }

    public boolean isProgressing(){
        return this.inProgress;
    }

    public String getLoadingTitle(){
        return this.progressTitle;
    }

    public String getLoadingText(){
        return this.progressLevel;
    }
}


