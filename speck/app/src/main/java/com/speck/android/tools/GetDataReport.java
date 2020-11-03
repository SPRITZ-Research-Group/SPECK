package com.speck.android.tools;

import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;

import com.speck.android.struct.AppDataModel;

import java.io.File;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class GetDataReport {
    private String msg;
    private String packageName;
    private  ApplicationInfo app;
    private PackageInfo pkgInfo;
    private PackageManager packageManager;

    public GetDataReport(String msg, String packageName, ApplicationInfo app, PackageInfo pkgInfo, PackageManager packageManager){
        this.msg = msg;
        this.packageName = packageName;
        this.app = app;
        this.pkgInfo = pkgInfo;
        this.packageManager = packageManager;
    }

    /**
     LoadData Issues
     **/

    public ArrayList<AppDataModel> getDataIssues(){
        try {
            ArrayList<AppDataModel> mylist = new ArrayList<>();

            String[] splitted = msg.split("&");
            int size = splitted.length;

            Map<String, List<String>> map = new HashMap<String, List<String>>();
            AppDataModel stats = null;

            // FETCH DATA
            for (int i = 0; i < size; i++){
                if (splitted[i].split("=")[0].equals("stats")){
                    stats = new AppDataModel(AppDataModel.SUMMARY_TYPE, splitted[i].split("=")[1]);
                } else if (splitted[i].split("=")[0].equals("criticals")
                        || splitted[i].split("=")[0].equals("warnings")
                        || splitted[i].split("=")[0].equals("infos")){

                    String[] elem = splitted[i].split("=")[1].split("\\+");

                    for (int j = 0; j < elem.length; j++){
                        String category = elem[j].split("@")[1];

                        if (map.get(category) == null){
                            List<String> val = new ArrayList<String>();
                            val.add(splitted[i].split("=")[0] + "=" + elem[j]);
                            map.put(category, val);
                        } else{
                            List<String> val = map.get(category);
                            val.add(splitted[i].split("=")[0] + "=" + elem[j]);
                            map.put(category, val);
                        }
                    }
                }
            }

            mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
            // STORE DATA
            mylist.add(new AppDataModel(AppDataModel.CATEGORY_TYPE, "Summary"));
            mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
            mylist.add(stats);

            mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
            for (Map.Entry<String, List<String>> entry : map.entrySet()) {
                String key = entry.getKey();
                List<String> values = entry.getValue();

                // add category
                mylist.add(new AppDataModel(AppDataModel.CATEGORY_TYPE, key));
                mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));

                // add items
                for (int i = 0; i < values.size(); i++){
                    mylist.add(new AppDataModel(AppDataModel.ITEM_TYPE, values.get(i)));

                    mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
                }
            }

            return mylist;

        } catch (Exception e){
            return null;
        }
    }

    /**
     LoadData General
     **/

    private String getInstallLocation(){
        if ((app.flags & ApplicationInfo.FLAG_EXTERNAL_STORAGE) != 0){
            return "External Storage";
        } else{
            return "Internal Storage";
        }
    }

    private double round(double value, int places) {
        if (places < 0) throw new IllegalArgumentException();

        long factor = (long) Math.pow(10, places);
        value = value * factor;
        long tmp = Math.round(value);
        return (double) tmp / factor;
    }

    public ArrayList<AppDataModel> getDataGeneral(){
        ArrayList<AppDataModel> mylist = new ArrayList<>();

        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "Application name@" + packageManager.getApplicationLabel(app)));
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "Package name@" + packageName));
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "Process name@" + app.processName));
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "Version name@" + pkgInfo.versionName));
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "Version code@" + pkgInfo.versionCode));
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "UID@" + app.uid));
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "Target SDK@" + app.targetSdkVersion));
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "Min SDK@" + app.minSdkVersion));
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "Apk path@ " + app.publicSourceDir));
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "Data path@ " + app.dataDir));
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));

        String location = getInstallLocation();
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "Install location@ " + location));
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));

        File file = new File(app.publicSourceDir);
        double size = round(file.length() / (1000000.0), 2);
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "Apk size@ " + String.valueOf(size).replace(".", ",") + " Mo"));
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));

        Calendar calendar = Calendar.getInstance();
        calendar.setTimeInMillis(pkgInfo.firstInstallTime);
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "First install@" + calendar.get(Calendar.DAY_OF_MONTH) + "/" + calendar.get(Calendar.MONTH) + " at " + calendar.get(Calendar.HOUR) + ":" + calendar.get(Calendar.MINUTE)));
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));

        calendar.setTimeInMillis(pkgInfo.lastUpdateTime);
        mylist.add(new AppDataModel(AppDataModel.GENERAL_TYPE, "Last update@" + calendar.get(Calendar.DAY_OF_MONTH) + "/" + calendar.get(Calendar.MONTH) + " at " + calendar.get(Calendar.HOUR) + ":" + calendar.get(Calendar.MINUTE)));


        return mylist;
    }

    /**
     LoadData Permissions
     **/

    public ArrayList<AppDataModel> getDataPermissions() {
        ArrayList<AppDataModel> mylist = new ArrayList<>();
        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));

        boolean isEmpty = true;

        if (pkgInfo.requestedPermissions != null) {
            isEmpty = false;
            for (int i = 0; i < pkgInfo.requestedPermissions.length; i++) {
                mylist.add(new AppDataModel(AppDataModel.PERMISSION_TYPE, pkgInfo.requestedPermissions[i]));
                mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
            }
        }

        if (pkgInfo.permissions != null) {
            for (int i = 0; i < pkgInfo.permissions.length - 1; i++) {
                isEmpty = false;
                mylist.add(new AppDataModel(AppDataModel.PERMISSION_TYPE, pkgInfo.permissions[i].name));
                mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));
            }
        }

        if (isEmpty){
            mylist.add(new AppDataModel(AppDataModel.EMPTY_TYPE, ""));
        }

        mylist.remove(mylist.size() -1);

        return mylist;
    }

    /**
     LoadData Activities
     **/

    public ArrayList<AppDataModel> getDataActivities(){
        ArrayList<AppDataModel> mylist = new ArrayList<>();

        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));

        if (pkgInfo.activities != null) {
            for (int i = 0; i < pkgInfo.activities.length; i++) {
                String parent = pkgInfo.activities[i].parentActivityName;
                String perm = pkgInfo.activities[i].permission;
                if (parent == null) {
                    parent = "N/A";
                }
                if (perm == null) {
                    perm = "none";
                }

                mylist.add(new AppDataModel(AppDataModel.ACTIVITY_TYPE, pkgInfo.activities[i].name + "@" + parent + "@" + perm + "@" + pkgInfo.activities[i].exported + "@" + packageName));
            }
        } else{
            mylist.add(new AppDataModel(AppDataModel.EMPTY_TYPE, ""));
        }

        return mylist;
    }

    /**
     LoadData Services
     **/

    public ArrayList<AppDataModel> getDataServices(){
        ArrayList<AppDataModel> mylist = new ArrayList<>();

        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));

        if (pkgInfo.services != null) {
            for (int i = 0; i < pkgInfo.services.length; i++) {
                String perm = pkgInfo.services[i].permission;
                String exported = "No";
                if (pkgInfo.services[i].exported) {
                    exported = "Yes";
                }
                if (perm == null) {
                    perm = "none";
                }

                mylist.add(new AppDataModel(AppDataModel.SERVICE_TYPE, pkgInfo.services[i].name + "@" + perm + "@" + exported));
            }
        } else{
            mylist.add(new AppDataModel(AppDataModel.EMPTY_TYPE, ""));
        }

        return mylist;
    }

    /**
     LoadData Providers
     **/

    public ArrayList<AppDataModel> getDataProviders(){
        ArrayList<AppDataModel> mylist = new ArrayList<>();

        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));

        if (pkgInfo.providers != null) {
            for (int i = 0; i < pkgInfo.providers.length; i++) {
                String read = pkgInfo.providers[i].readPermission;
                String write = pkgInfo.providers[i].writePermission;
                String exported = "No";
                if (pkgInfo.providers[i].exported) { exported = "Yes"; }
                if (read == null) { read = "none"; }
                if (write == null) { write = "none"; }

                mylist.add(new AppDataModel(AppDataModel.PROVIDER_TYPE, pkgInfo.providers[i].name + "@" + read + "@" + write + "@" + exported));
            }
        } else{
            mylist.add(new AppDataModel(AppDataModel.EMPTY_TYPE, ""));
        }

        return mylist;
    }

    /**
     LoadData Receivers
     **/

    public ArrayList<AppDataModel> getDataReceivers(){
        ArrayList<AppDataModel> mylist = new ArrayList<>();

        mylist.add(new AppDataModel(AppDataModel.DIVIDER_TYPE, ""));

        if (pkgInfo.receivers != null) {
            for (int i = 0; i < pkgInfo.receivers.length; i++) {
                String perm = pkgInfo.receivers[i].permission;
                String exported = "No";
                if (pkgInfo.receivers[i].exported) {
                    exported = "Yes";
                }
                if (perm == null) {
                    perm = "none";
                }

                mylist.add(new AppDataModel(AppDataModel.RECEIVER_TYPE, pkgInfo.receivers[i].name + "@" + perm + "@" + exported));
            }
        } else{
            mylist.add(new AppDataModel(AppDataModel.EMPTY_TYPE, ""));
        }

        return mylist;
    }

}
