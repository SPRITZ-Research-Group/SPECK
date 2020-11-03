package com.speck.android;

import android.os.Bundle;
import android.view.View;
import androidx.recyclerview.widget.OrientationHelper;
import java.util.ArrayList;
import androidx.recyclerview.widget.RecyclerView;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.DefaultItemAnimator;
import androidx.fragment.app.Fragment;
import android.view.LayoutInflater;
import android.view.ViewGroup;

import com.speck.android.adapter.IssueAdapter;
import com.speck.android.struct.AppDataModel;

public class ResultsFragment extends Fragment{

    private ArrayList<AppDataModel> list;

    private RecyclerView rv;
    private View myView;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        myView = inflater.inflate(R.layout.results_layout,container,false);
        list = ReportActivity.getListResults();

        // RecyclerView
        IssueAdapter mAdapter = new IssueAdapter(list, getContext());
        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(getContext(), OrientationHelper.VERTICAL, false);

        rv = (RecyclerView) myView.findViewById(R.id.list_report);
        rv.setLayoutManager(linearLayoutManager);
        rv.setItemAnimator(new DefaultItemAnimator());
        rv.setAdapter(mAdapter);

        return myView;
    }
}

