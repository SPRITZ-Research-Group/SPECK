package com.speck.android;

import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import com.google.android.material.snackbar.Snackbar;
import com.google.android.material.tabs.TabLayout;
import androidx.viewpager.widget.ViewPager;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.ImageView;

import com.speck.android.adapter.ReportHolder;
import com.speck.android.struct.AppDataModel;
import com.speck.android.tools.FileReader;
import com.speck.android.tools.GetDataReport;

import java.io.File;
import java.util.ArrayList;

public class ReportActivity extends AppCompatActivity {

    private String packageName;
    private String position;
    private ApplicationInfo app;
    private PackageInfo pkgInfo;
    private PackageManager packageManager;
    public static String msg;

    private static ArrayList<AppDataModel> list_results;
    private static ArrayList<AppDataModel> list_general;
    private static ArrayList<AppDataModel> list_permissions;
    private static ArrayList<AppDataModel> list_activities;
    private static ArrayList<AppDataModel> list_services;
    private static ArrayList<AppDataModel> list_providers;
    private static ArrayList<AppDataModel> list_receivers;

    private static ViewPager viewPager;
    private TabLayout tabLayout;
    private Context ctx;

    private ResultsFragment resultsFragment = new ResultsFragment();
    private GeneralFragment generalFragment = new GeneralFragment();
    private PermissionsFragment permissionsFragment = new PermissionsFragment();
    private ActivitiesFragment activitiesFragment = new ActivitiesFragment();
    private ServicesFragment servicesFragment = new ServicesFragment();
    private ProvidersFragment providersFragment = new ProvidersFragment();
    private ReceiversFragment receiversFragment = new ReceiversFragment();

    private GetDataReport getData;

    public static final String MANIFEST_DATA = "com.speck.android.MANIFEST_DATA";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_report);
        ctx = this;

        initActivity();
        new ReportActivity.LoadData().executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);

        // ViewPager
        viewPager = (ViewPager) findViewById(R.id.viewpager);
        setupViewPager(viewPager);
        tabLayout = (TabLayout) findViewById(R.id.tabs);
        tabLayout.setupWithViewPager(viewPager);
    }


    public void setupViewPager(ViewPager viewPager){
        ReportHolder pagerAdapter = new ReportHolder(getSupportFragmentManager());

        pagerAdapter.addFragment(generalFragment,"General");
        pagerAdapter.addFragment(resultsFragment,"Security analysis");
        pagerAdapter.addFragment(permissionsFragment,"Permissions");
        pagerAdapter.addFragment(activitiesFragment,"Activities");
        pagerAdapter.addFragment(servicesFragment,"Services");
        pagerAdapter.addFragment(providersFragment,"Content providers");
        pagerAdapter.addFragment(receiversFragment,"Broadcast receivers");

        viewPager.setAdapter(pagerAdapter);
    }

    private void initActivity(){
        // Get the Intent which started this activity and extract the string
        Intent intent = getIntent();
        String message = intent.getStringExtra(ApplicationsFragment.SERVER_MESSAGE);
        position = intent.getStringExtra(ApplicationsFragment.REQUEST_ID);

        // Extract Data Info
        extractPkg(message);

        // InitToolbar
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        getSupportActionBar().setDisplayShowHomeEnabled(true);
        getSupportActionBar().setTitle(packageName);

        packageManager = this.getPackageManager();
        try {
            app = packageManager.getApplicationInfo(packageName, 0);
            pkgInfo = packageManager.getPackageInfo(packageName, PackageManager.GET_PERMISSIONS |
                                                                    PackageManager.GET_ACTIVITIES |
                                                                    PackageManager.GET_SERVICES |
                                                                    PackageManager.GET_PROVIDERS |
                                                                    PackageManager.GET_RECEIVERS);

            ((ImageView) findViewById(R.id.icon_report)).setImageDrawable(app.loadIcon(packageManager));

        } catch(PackageManager.NameNotFoundException e){
            Log.e("Exception found ",e.getMessage());
            AlertDialog alertDialog = new AlertDialog.Builder(ctx)
                    .setMessage("Package name not found")
                    .setTitle("An error occurred").setCancelable(false)
                    .setNegativeButton("OK",
                            new DialogInterface.OnClickListener() {
                                public void onClick(DialogInterface dialog, int which) {
                                    dialog.dismiss();
                                    finish();
                                }
                            })
                    .show();
        }

        getData = new GetDataReport(msg, packageName, app, pkgInfo, packageManager);
    }

    private void extractPkg(String input){
        FileReader fileReader = new FileReader(this, input);
        String message = fileReader.read();

        String[] splitted = message.split("&");

        try {
            this.packageName = splitted[0].split("=")[1];
        } catch (Exception e){
            this.packageName = "";
        }

        this.msg = message;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        String versionName = "";
        try {
            versionName = this.getPackageManager().getPackageInfo(packageName, 0).versionName;
        } catch(PackageManager.NameNotFoundException e) {
            Log.e("Exception found ", e.getMessage());
        }

        switch (item.getItemId()){
            case R.id.action_reload:
                setResult(ApplicationsFragment.RESULT_OK,
                        new Intent().putExtra(ApplicationsFragment.REQUEST_ID, position));
                finish();
                return true;

            case R.id.action_remove:
                FileReader fr = new FileReader(this);
                fr.deleteFile(packageName + "_" + versionName);
                fr.deleteFile("manifest_" + packageName + "_" + versionName + ".xml");
                setResult(ApplicationsFragment.RESULT_OK_REMOVE,
                        new Intent().putExtra(ApplicationsFragment.REQUEST_ID, position));
                finish();
                return true;

            case R.id.action_info:
                try {
                    Intent intent = new Intent(android.provider.Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
                    intent.setData(Uri.parse("package:" + packageName));
                    startActivity(intent);
                } catch ( ActivityNotFoundException e ) {
                    Intent intent = new Intent(android.provider.Settings.ACTION_MANAGE_APPLICATIONS_SETTINGS);
                    startActivity(intent);
                }
                return true;

            case R.id.action_export:
                try {
                    ApplicationInfo app = getPackageManager().getApplicationInfo(packageName, 0);
                    String apkPath = app.sourceDir;

                    Intent intentShareFile = new Intent(Intent.ACTION_SEND);
                    File fileWithinMyDir = new File(apkPath);

                    if(fileWithinMyDir.exists()) {
                        intentShareFile.setType("application/vnd.android.package-archive");
                        intentShareFile.putExtra(Intent.EXTRA_STREAM, Uri.parse("file://"+apkPath));

                        intentShareFile.putExtra(Intent.EXTRA_SUBJECT,"APK " + packageName);

                        startActivity(Intent.createChooser(intentShareFile, "Share File"));
                    }
                } catch (PackageManager.NameNotFoundException e){ Log.e("Exception found ", e.getMessage()); }

                return true;

            case R.id.action_google:
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=" + packageName)));
                } catch (android.content.ActivityNotFoundException e) {
                    startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://play.google.com/store/apps/details?id=" + packageName)));
                }
                return true;

            case R.id.action_display_xml:
                FileReader reader = new FileReader(this);

                if (reader.fileExists("manifest_" + packageName + "_" + versionName + ".xml")) {
                    Intent intent = new Intent(this, ManifestActivity.class);
                    intent.putExtra(ReportActivity.MANIFEST_DATA, "manifest_" + packageName + "_" + versionName + ".xml");
                    startActivity(intent);
                } else{
                    Snackbar.make(ReportActivity.viewPager.getFocusedChild(), "No AndroidManifest.xml found", Snackbar.LENGTH_LONG)
                            .setAction("Action", null).show();
                }
                return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_report, menu);
        return true;
    }

    @Override
    public void onBackPressed() {
        finish();
    }

    /**
     LoadData
     **/

    private class LoadData extends AsyncTask<Void, Void, Void> {

        private ProgressDialog progress = null;

        @Override
        protected Void doInBackground(Void... params) {
            Log.i("********", "test1");

            list_results = getData.getDataIssues();
            list_general = getData.getDataGeneral();
            list_permissions = getData.getDataPermissions();
            list_activities = getData.getDataActivities();
            list_services = getData.getDataServices();
            list_providers = getData.getDataProviders();
            list_receivers = getData.getDataReceivers();

            Log.i("********", "test2");
            if (list_results == null){
                Log.i("********", "test3");
                progress.dismiss();
//                AlertDialog alertDialog = new AlertDialog.Builder(ctx)
//                        .setMessage("Data corrupted")
//                        .setTitle("An error occurred").setCancelable(false)
//                        .setNegativeButton("OK",
//                                new DialogInterface.OnClickListener() {
//                                    public void onClick(DialogInterface dialog, int which) {
//                                        dialog.dismiss();
//                                        finish();
//                                    }
//                                })
//                        .show();
                Log.i("********", "test4");
            }

            return null;
        }

        @Override
        protected void onPostExecute(Void result) {
            progress.dismiss();
            super.onPostExecute(result);
        }

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            progress = ProgressDialog.show(ctx, null, "Loading...");
        }
    }

    public static ArrayList<AppDataModel> getListResults(){
        return list_results;
    }

    public static ArrayList<AppDataModel> getListGeneral(){
        return list_general;
    }

    public static ArrayList<AppDataModel> getListPermissions(){
        return list_permissions;
    }

    public static ArrayList<AppDataModel> getListActivities(){
        return list_activities;
    }

    public static ArrayList<AppDataModel> getListServices(){
        return list_services;
    }

    public static ArrayList<AppDataModel> getListProviders(){
        return list_providers;
    }

    public static ArrayList<AppDataModel> getListReceivers(){
        return list_receivers;
    }

}
