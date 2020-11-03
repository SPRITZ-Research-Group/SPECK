package com.speck.android;

import android.app.Fragment;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import androidx.annotation.Nullable;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

public class AboutFragment extends Fragment {

    View myView;

    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState){
        myView = inflater.inflate(R.layout.about_layout, container, false);

        TextView link = (TextView) myView.findViewById(R.id.src_code);
        link.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent i = new Intent(Intent.ACTION_VIEW);
                i.setData(Uri.parse("https://bitbucket.org/elosiouk/android_s_p_guidelines/src/master/"));
                startActivity(i);
            }
        });

        return myView;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setHasOptionsMenu(true);
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
        item5.setVisible(false);
    }

}