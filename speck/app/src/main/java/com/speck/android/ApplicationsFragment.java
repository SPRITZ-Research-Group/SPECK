package com.speck.android;

import android.app.Fragment;
import android.content.Context;
import android.content.SharedPreferences;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Bundle;
import android.preference.PreferenceManager;
import androidx.annotation.Nullable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.Toast;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import android.app.ProgressDialog;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.os.AsyncTask;
import android.widget.ListView;
import android.content.pm.PackageManager.NameNotFoundException;
import android.content.Intent;
import android.util.Log;
import android.os.Messenger;
import android.os.Message;
import android.os.Handler;
import android.app.AlertDialog;
import android.content.DialogInterface;
import com.google.android.material.snackbar.Snackbar;


import com.speck.android.adapter.AppAdapter;
import com.speck.android.struct.AppItem;
import com.speck.android.tools.CustomAnimator;
import com.speck.android.tools.FileReader;
import com.speck.android.tools.ServerCommunication;

public class ApplicationsFragment extends Fragment implements OnItemClickListener {

    private View myView;
    private ListView listview;
    private AppAdapter mAdapter;

    // MAIN DATA
    public static ArrayList<AppItem> mainList = null;
    private static ArrayList<AppItem> mainListComplete = null;
    private static ArrayList<AppItem> mainListCategory = null;
    public static ArrayList<ServerCommunication> socketList;

    // OBJECT STATE
    private static boolean wasInstantiated = false;
    private static boolean reload = true;
    private boolean dialogIsShowing = false;
    private static int CURRENT_REQUEST_NB = 0;
    private List<Integer> listPositions = new ArrayList<Integer>();
    private List<Integer> listPosAnimated = new ArrayList<>();

    // TOOLS
    private CustomAnimator animator;
    public Handler messageHandler = new MessageHandler();
    private PackageManager packageManager = null;
    private int currentSortCtgy = SORT_ALL;
    private String currentQuery = "";

    // CONSTANTS
    public static final String SERVER_MESSAGE = "com.speck.android.SERVER_MESSAGE";
    public static final String SERVER_REQUEST = "com.speck.android.SERVER_REQUEST";
    public static final String MESSENGER = "com.speck.android.SERVER_MESSENGER";
    public static final String REQUEST_ID = "com.speck.android.REQUEST_ID";

    public static final int SORT_SEARCH = -133122;
    public static final int SORT_ALL = -1331234;
    public static final int SORT_ANALYSED = -92233;
    public static final int SORT_NOT_ANALYSED = -1338882;
    public static final int SORT_IN_PROGRESS = -134443;

    public static final int REQUEST_REPORT_ID = 123131;
    public static final int RESULT_OK = 1;
    public static final int RESULT_OK_REMOVE = 2;

    private final int MAX_REQUEST = 3;

    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState){
        myView = inflater.inflate(R.layout.applications_layout, container, false);
        animator = new CustomAnimator(MainActivity.getMainContext());

        /* Set ListView */
        listview = (ListView) myView.findViewById(R.id.list_applications);
        listview.setOnItemClickListener(new OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, final View view,
                                    int position, long id) {

                AppItem app = mainList.get(position);
                final int realPosition = getRealPosition(app);

                if (CURRENT_REQUEST_NB >= MAX_REQUEST){
                    animate(view, realPosition);
                    Snackbar.make(view, "You can make only " + MAX_REQUEST + " requests at a time", Snackbar.LENGTH_LONG)
                            .setAction("Action", null).show();

                } else if (app.wasAnalysed()) {
                    Intent intent = new Intent(getActivity(), ReportActivity.class);
                    intent.putExtra(ApplicationsFragment.SERVER_MESSAGE, app.getFileName());

                    intent.putExtra(ApplicationsFragment.REQUEST_ID, String.valueOf(realPosition));

                    startActivityForResult(intent, REQUEST_REPORT_ID);

                } else if (!listPositions.contains(realPosition)){
                    animate(view, realPosition);
                    // check Wi-Fi connection if APK Uploading is set
                    SharedPreferences sharedPref = PreferenceManager.getDefaultSharedPreferences(MainActivity.getMainContext());
                    boolean option = sharedPref.getBoolean("checkboxPref", false);
                    ConnectivityManager cm = (ConnectivityManager)MainActivity.getMainContext().getSystemService(Context.CONNECTIVITY_SERVICE);
                    NetworkInfo activeNetwork = cm.getActiveNetworkInfo();

                    if (!option || (option && (activeNetwork.getType() == ConnectivityManager.TYPE_WIFI))) {
                        runService(realPosition, app);
                    } else{
                        Snackbar.make(view, "You must be connected to a Wi-Fi hotspot. Otherwise, go to the settings", Snackbar.LENGTH_LONG)
                                .setAction("Action", null).show();
                    }
                } else{
                    if (socketList.get(realPosition) != null && !mainListComplete.get(realPosition).getLoadingTitle().equals("1/4")) {
                        socketList.get(realPosition).close();
                        socketList.set(realPosition, null);
                        Snackbar.make(view, "Analysis canceled", Snackbar.LENGTH_LONG)
                                .setAction("Action", null).show();
                    }
                }
            }
        });

        /* RUN */
        packageManager = getActivity().getPackageManager();

        if (existed() && !reload){
            mainList = new ArrayList<>(mainListComplete);
            mAdapter = new AppAdapter(getActivity());
            listview.setAdapter(mAdapter);
        } else {
            new LoadApplications(true).executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
            reload = false;
        }

        wasInstantiated = true;

        return myView;
    }

    public void animate(final View view, final int realPosition){
        listPosAnimated.add(realPosition);
        view.animate().setDuration(150).alpha(0).
                withEndAction(new Runnable() {
                    @Override
                    public void run() {
                        mAdapter.notifyDataSetChanged();
                        view.animate().setDuration(150).alpha(1).
                                withEndAction(new Runnable() {
                                    @Override
                                    public void run() {
                                        mAdapter.notifyDataSetChanged();
                                        listPosAnimated.remove(new Integer(realPosition));
                                        view.setAlpha(1);
                                    }
                                });
                    }
                });
    }

    public void runService(int realPosition, AppItem app){
        CURRENT_REQUEST_NB += 1;
        listPositions.add(realPosition);

        app.setProgress(true, "1/4", "Reaching server...");
        if (!listPosAnimated.contains(realPosition)) {
            mAdapter.notifyDataSetChanged();
        }
        //Toast.makeText(mainContext, "The process has started. Please wait...", Toast.LENGTH_LONG).show();

        // Get data to send to the Service
        String request = makeRequest(app);

        Intent intent = new Intent(getActivity(), DownloaderService.class);
        intent.putExtra(ApplicationsFragment.SERVER_REQUEST, request);
        intent.putExtra(ApplicationsFragment.MESSENGER, new Messenger(messageHandler));

        intent.putExtra(ApplicationsFragment.REQUEST_ID, String.valueOf(realPosition));
        getActivity().startService(intent);
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_REPORT_ID && resultCode == RESULT_OK) {
            int pos = Integer.parseInt(data.getStringExtra(ApplicationsFragment.REQUEST_ID));
            AppItem app = mainListComplete.get(pos);
            app.setAnalyse(false);
            setQuery(currentQuery, currentSortCtgy);
            runService(pos, app);
        }
        if (requestCode == REQUEST_REPORT_ID && resultCode == RESULT_OK_REMOVE) {
            int pos = Integer.parseInt(data.getStringExtra(ApplicationsFragment.REQUEST_ID));
            AppItem app = mainListComplete.get(pos);
            app.setAnalyse(false);
            setQuery(currentQuery, currentSortCtgy);
        }
    }

    @Override
    public void onActivityCreated(Bundle savedInstanceState) {
        super.onActivityCreated(savedInstanceState);
    }

    @Override
    public void onItemClick(AdapterView<?> parent, View view, int position,long id) {
        //Toast.makeText(getActivity(), "Item: " + position, Toast.LENGTH_SHORT).show();
    }

    public View getView(){
        return myView;
    }

    public static boolean isAnalysing(){
        if (CURRENT_REQUEST_NB == 0){
            return false;
        }
        return true;
    }

    public static boolean existed(){
        return wasInstantiated;
    }

    public void setRefresh(){
        reload = true;
    }

    private int getRealPosition(AppItem app){
        int real = 0;
        int size = mainListComplete.size();
        for (int i = 0; i < size; i++){
            if (mainListComplete.get(i).getPkg().equals(app.getPkg())){
                real = i;
                break;
            }
        }
        return real;
    }

    @Override
    public void onStop(){
        currentQuery = "";
        currentSortCtgy = SORT_ALL;
        super.onStop();
    }

    /**
     Manage SearchView
     **/

    public void setQuery(String query, int type){

        currentQuery = query;
        currentSortCtgy = type;

        if (type == ApplicationsFragment.SORT_SEARCH){
            int size = mainListCategory.size();
            mainList.clear();

            for (int i = 0; i < size; i++) {
                String appName = mainListCategory.get(i).getAppName();
                if (appName.toLowerCase().contains(query.toLowerCase())) {
                    mainList.add(mainListCategory.get(i));
                }
            }

        } else{
            int size = mainListComplete.size();
            mainList.clear();

            for (int i = 0; i < size; i++) {
                if (type == ApplicationsFragment.SORT_ANALYSED && mainListComplete.get(i).wasAnalysed()) {
                    mainList.add(mainListComplete.get(i));
                } else if (type == ApplicationsFragment.SORT_ALL) {
                    mainList.add(mainListComplete.get(i));
                } else if (type == ApplicationsFragment.SORT_NOT_ANALYSED && !mainListComplete.get(i).wasAnalysed()) {
                    mainList.add(mainListComplete.get(i));
                } else if (type == ApplicationsFragment.SORT_IN_PROGRESS && mainListComplete.get(i).isProgressing()) {
                    mainList.add(mainListComplete.get(i));
                }
            }
            mainListCategory = new ArrayList<>(mainList);
        }

        if (mainList.size() == 0){
            listview.setEmptyView(getView().findViewById(R.id.emptyElement));
        } else{
            //listview.setAdapter(mAdapter);
        }
        mAdapter.notifyDataSetChanged();
    }

    /**
     Manage Service
     **/

    @Override
    public void onDestroy(){
        super.onDestroy();
        getActivity().stopService(new Intent(getActivity(), DownloaderService.class));
    }

    // Method to stop the service
    public void stopService() {
        getActivity().stopService(new Intent(getActivity(), DownloaderService.class));
    }

    /**
     Manage Service replies
     **/

    public class MessageHandler extends Handler {
        @Override
        public void handleMessage(Message message) {
            String reply = (String) message.obj;

            int position = Integer.parseInt(reply.split("&")[0].split("=")[1]);

            // ERROR
            if (reply.split("&")[1].split("=")[0].equals("error")) {

                if (dialogIsShowing == false) {
                    dialogIsShowing = true;

                    if (!reply.split("&")[1].split("=")[1].equals("No reply from the server.")) {
                        AlertDialog alertDialog = new AlertDialog.Builder(MainActivity.getMainContext())
                                .setMessage(reply.split("&")[1].split("=")[1])
                                .setTitle("An error occurred").setCancelable(false)
                                .setNegativeButton("OK",
                                        new DialogInterface.OnClickListener() {
                                            public void onClick(DialogInterface dialog, int which) {
                                                dialog.dismiss();
                                                dialogIsShowing = false;
                                            }
                                        })
                                .show();
                    } else{
                        dialogIsShowing = false;
                    }
                }

                mainListComplete.get(position).setProgress(false, "", "");

                FileReader fr = new FileReader(MainActivity.getMainContext());
                String filename = reply.split("&")[2].split("=")[1];
                if (fr.fileExists(filename)){
                    mainListComplete.get(position).setAnalyse(true);
                }

                setQuery(currentQuery, currentSortCtgy);

                // STATUS UPDATE
            } else if (reply.split("&")[1].split("=")[0].equals("status")){
                mainListComplete.get(position).setProgress(true,
                        reply.split("&")[2].split("=")[1] + "/4",
                        reply.split("&")[1].split("=")[1]+"...");

                if (!listPosAnimated.contains(position)) {
                    mAdapter.notifyDataSetChanged();
                }

                // CORRECT
            } else{
                mainListComplete.get(position).setProgress(false, "", "");
                mainListComplete.get(position).setAnalyse(true);
                setQuery(currentQuery, currentSortCtgy);
                Toast.makeText(MainActivity.getMainContext(), mainListComplete.get(position).getAppName() + " analysed", Toast.LENGTH_LONG).show();
            }

            // CONTROL
            if (!reply.split("&")[1].split("=")[0].equals("status")) {
                for (int i = 0; i < listPositions.size(); i++) {
                    if (listPositions.get(i) == position) {
                        listPositions.remove(i);
                        break;
                    }
                }
                CURRENT_REQUEST_NB -= 1;
            }
            //Log.e("DEBUG --> ", reply);
        }
    }

    /**
     Make Server Request
     **/

    private String sanitizeVar(String msg){
        msg = msg.replace("&", "and");
        msg = msg.replace("+", "plus");
        msg = msg.replace("=", "eq");
        return msg;
    }

    private String getApkDir(String pkg){
        String apkPath = "";
        try {
            ApplicationInfo app = packageManager.getApplicationInfo(pkg, 0);
            apkPath = app.sourceDir;
        } catch (PackageManager.NameNotFoundException e){
            Log.e("Exception found ", e.getMessage());
        }
        return apkPath;
    }

    private String makeRequest(AppItem app){

        String packageName = app.getPkg();
        String appName = app.getAppName();
        String versionName = app.getVersion();

        packageName = sanitizeVar(packageName);
        appName = sanitizeVar(appName);
        versionName = sanitizeVar(versionName);

        File f = new File(getApkDir(packageName));
        return "packageName="+packageName+"&"+"versionName="+versionName+"&appName="+appName+"&fileSize="+String.valueOf(f.length());
    }

    public String getVersion(ApplicationInfo app){
        String versionName = "";
        try {
            versionName = getActivity().getPackageManager().getPackageInfo(app.packageName, 0).versionName;
        } catch(NameNotFoundException e) {
            Log.e("Exception found ", e.getMessage());
        }
        return versionName;
    }

    /**
     LoadApplications
     **/

    private List<ApplicationInfo> checkForLaunchIntent(List<ApplicationInfo> list) {

        ArrayList<ApplicationInfo> appList = new ArrayList<>();

        for(ApplicationInfo info : list) {
            try{
                if(packageManager.getLaunchIntentForPackage(info.packageName) != null) {
                    // Check if it's not a system package
                    if ((info.flags & ApplicationInfo.FLAG_SYSTEM) == 0) {
                        appList.add(info);
                    }
                }
            } catch(Exception e) {
                e.printStackTrace();
            }
        }

        return appList;
    }

    private void clearInternalStorage(){
        File dir = MainActivity.getMainContext().getFilesDir();
        File[] files = dir.listFiles();

        int mainLen = mainListComplete.size();
        int filesLen = files.length;
        boolean wasFound;

        for (int j = 0; j < filesLen; j++) {
            wasFound = false;
            for (int i = 0; i < mainLen; i++) {
                AppItem app = mainListComplete.get(i);
                if (app.getFileNameToFind().equals(files[j].getName()) || app.getManifest().equals(files[j].getName())){
                    wasFound = true;
                    break;
                }
            }

            if (!wasFound){
                Log.e("DELETED --->", files[j].getName());
                FileReader toDel = new FileReader(MainActivity.getMainContext());
                toDel.deleteFile(files[j].getName());
            }
        }
    }

    private class LoadApplications extends AsyncTask<Void, Void, Void> {

        private ProgressDialog progress = null;
        private boolean showProgress;

        private LoadApplications(boolean showProgress){
            this.showProgress = showProgress;
        }

        @Override
        protected Void doInBackground(Void... params) {
            List<ApplicationInfo> appList = checkForLaunchIntent(packageManager.getInstalledApplications(PackageManager.GET_META_DATA));

            mainList = new ArrayList<>();
            socketList = new ArrayList<>();

            for (int i = 0; i < appList.size(); i++){
                ApplicationInfo app = appList.get(i);
                AppItem item = new AppItem(getActivity(),
                        (String)app.loadLabel(packageManager),
                        app.packageName, getVersion(app),
                        app.loadIcon(packageManager));
                mainList.add(item);
                socketList.add(null);
            }

            mainListComplete = new ArrayList<>(mainList);
            mainListCategory = new ArrayList<>(mainList);

            clearInternalStorage();

            return null;
        }

        @Override
        protected void onPostExecute(Void result) {
            mAdapter = new AppAdapter(getActivity());
            listview.setAdapter(mAdapter);

            animator.startAnimation(myView, 600, R.anim.fade_in);

            if (this.showProgress) {
                progress.dismiss();
            }
            super.onPostExecute(result);
        }

        @Override
        protected void onPreExecute() {
            if (this.showProgress) {
                progress = ProgressDialog.show(getActivity(), null, "Loading apps info...");
            }
            super.onPreExecute();
        }
    }

}
