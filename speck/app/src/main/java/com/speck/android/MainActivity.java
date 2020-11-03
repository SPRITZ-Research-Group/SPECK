package com.speck.android;

import android.app.AlertDialog;
import android.app.FragmentManager;
import android.app.NotificationManager;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;

import com.google.android.material.snackbar.Snackbar;
import androidx.core.view.MenuItemCompat;
import androidx.appcompat.widget.SearchView;

import android.preference.PreferenceManager;
import com.google.android.material.navigation.NavigationView;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;
import androidx.appcompat.app.ActionBarDrawerToggle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity
        implements NavigationView.OnNavigationItemSelectedListener {

    private ApplicationsFragment applicationsFragment = new ApplicationsFragment();
    private SearchView searchView;
    private NavigationView navigationView;
    private static Context ctx;
    private Menu main_menu;

    public static boolean isRunning;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        ctx = this;

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.addDrawerListener(toggle);
        toggle.syncState();

        navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        FragmentManager fragmentManager = getFragmentManager();
        fragmentManager.beginTransaction().replace(R.id.content_frame, applicationsFragment).commit();
        navigationView.setCheckedItem(R.id.nav_applications);

    }

    public static Context getMainContext(){
        return ctx;
    }

    @Override
    public void onBackPressed() {
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else if (!searchView.isIconified()) {
            searchView.setIconified(true);
            searchView.clearFocus();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    public void onStart(){
        super.onStart();
        isRunning = true;
    }

    @Override
    public void onStop(){
        super.onStop();
        isRunning = false;
    }

    @Override
    public void onDestroy(){
        NotificationManager mNotificationManager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        mNotificationManager.cancelAll();
        super.onDestroy();
    }

    /**
     Menu
     **/

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main, menu);
        main_menu = menu;

        searchView = (SearchView) MenuItemCompat.getActionView(menu.findItem(R.id.action_search));
        searchView.setQueryHint("Search");
        searchView.setOnQueryTextListener(new SearchView.OnQueryTextListener() {
            @Override
            public boolean onQueryTextSubmit(String query) {
                searchView.clearFocus();
                return false;
            }

            @Override
            public boolean onQueryTextChange(String newText) {
                applicationsFragment.setQuery(newText, ApplicationsFragment.SORT_SEARCH);
                return false;
            }
        });

        searchView.setOnCloseListener(new SearchView.OnCloseListener() {
            @Override
            public boolean onClose() {
                //main_menu.findItem(R.id.sort_app_all).setChecked(true);
                return false;
            }
        });

        return true;
    }

    @Override
    public boolean onPrepareOptionsMenu(Menu menu) {
        MenuItem item = menu.findItem(R.id.action_reset);
        item.setVisible(false);

        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();

        if (id == R.id.action_howto) {
            new AlertDialog.Builder(ctx)
                    .setTitle("Info")
                    .setMessage("Select one or more applications in the list that you want analyzed by our servers. Be careful, it can take several minutes !")
                    .setCancelable(true)
                    .setNegativeButton("OK", null)
                    .show();
            return true;

        } else if (id == R.id.action_refresh) {
            if (!ApplicationsFragment.isAnalysing()) {
                FragmentManager fragmentManager = getFragmentManager();
                applicationsFragment = new ApplicationsFragment();
                applicationsFragment.setRefresh();
                main_menu.findItem(R.id.sort_app_all).setChecked(true);
                fragmentManager.beginTransaction().replace(R.id.content_frame, applicationsFragment).commit();
            } else{
                Snackbar.make(applicationsFragment.getView(), "Please wait for the end of the analyzes", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
            }

        } else if (id == R.id.sort_app_all){
            item.setChecked(true);
            applicationsFragment.setQuery("", ApplicationsFragment.SORT_ALL);

        } else if (id == R.id.sort_app_analysed){
            item.setChecked(true);
            applicationsFragment.setQuery("", ApplicationsFragment.SORT_ANALYSED);

        } else if (id == R.id.sort_app_not_analysed){
            item.setChecked(true);
            applicationsFragment.setQuery("", ApplicationsFragment.SORT_NOT_ANALYSED);

        } else if (id == R.id.sort_app_analysing){
            item.setChecked(true);
            applicationsFragment.setQuery("", ApplicationsFragment.SORT_IN_PROGRESS);
        } else if (id == R.id.action_reset){
            SharedPreferences sharedPref = PreferenceManager.getDefaultSharedPreferences(getBaseContext());
            SharedPreferences.Editor editor = sharedPref.edit();
            editor.putString("ip", getString(R.string.default_ip));
            editor.putString("port", getString(R.string.default_port));
            editor.putBoolean("checkboxPref", true);
            editor.commit();

            FragmentManager fragmentManager = getFragmentManager();
            fragmentManager.beginTransaction().replace(R.id.content_frame, new SettingsFragment()).commit();

            Toast.makeText(MainActivity.getMainContext(), "Settings restored", Toast.LENGTH_LONG).show();
        }

        return super.onOptionsItemSelected(item);
    }

    /**
     Navigation Drawer
     **/

    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();
        FragmentManager fragmentManager = getFragmentManager();

        if (id == R.id.nav_applications) {
            fragmentManager.beginTransaction().replace(R.id.content_frame, applicationsFragment).commit();
        } else if (id == R.id.nav_settings) {
            fragmentManager.beginTransaction().replace(R.id.content_frame, new SettingsFragment()).commit();
        } else if (id == R.id.nav_about) {
            fragmentManager.beginTransaction().replace(R.id.content_frame, new AboutFragment()).commit();
        } else{
            Snackbar.make(applicationsFragment.getView(), "Please wait for the end of the analyzes", Snackbar.LENGTH_LONG)
                    .setAction("Action", null).show();
            DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
            drawer.closeDrawer(GravityCompat.START);
            return false;
        }

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }
}
