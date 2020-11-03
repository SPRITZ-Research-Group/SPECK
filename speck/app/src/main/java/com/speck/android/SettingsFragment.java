package com.speck.android;

import android.os.Bundle;
import android.preference.PreferenceFragment;
import android.view.Menu;
import android.view.MenuItem;

public class SettingsFragment extends PreferenceFragment {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setHasOptionsMenu(true);
        addPreferencesFromResource(R.xml.preferences);
    }

    @Override
    public void onPrepareOptionsMenu(Menu menu) {
        MenuItem item = menu.findItem(R.id.action_howto);
        item.setVisible(false);

        MenuItem item2 = menu.findItem(R.id.action_refresh);
        item2.setVisible(false);

        MenuItem item3 = menu.findItem(R.id.action_search);
        item3.setVisible(false);

        MenuItem item4 = menu.findItem(R.id.action_sort);
        item4.setVisible(false);

        MenuItem item5 = menu.findItem(R.id.action_reset);
        item5.setVisible(true);
    }

}