package com.speck.android;

import android.os.Bundle;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.DefaultItemAnimator;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.OrientationHelper;
import androidx.recyclerview.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.speck.android.adapter.IssueAdapter;
import com.speck.android.struct.AppDataModel;

import java.util.ArrayList;

public class ActivitiesFragment  extends Fragment {
    private ArrayList<AppDataModel> list;

    private RecyclerView rv;
    private View myView;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        myView = inflater.inflate(R.layout.general_layout,container,false);
        list = ReportActivity.getListActivities();

        // RecyclerView
        IssueAdapter mAdapter = new IssueAdapter(list, getContext());
        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(getContext(), OrientationHelper.VERTICAL, false);

        rv = (RecyclerView) myView.findViewById(R.id.list_general);
        rv.setLayoutManager(linearLayoutManager);
        rv.setItemAnimator(new DefaultItemAnimator());
        rv.setAdapter(mAdapter);

        return myView;
    }


}
