package com.speck.android.adapter;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.ImageView;
import android.util.Log;

import com.speck.android.ApplicationsFragment;
import com.speck.android.R;
import com.speck.android.struct.AppItem;

public class AppAdapter extends BaseAdapter{

    private LayoutInflater mInflater;

    public AppAdapter(Context context) {
        mInflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
    }

    @Override
    public int getCount() {
        return ApplicationsFragment.mainList.size();
    }

    @Override
    public AppItem getItem(int position) {
        return ApplicationsFragment.mainList.get(position);
    }

    @Override
    public long getItemId(int position) {
        return position;
    }

    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder = null;

        if (convertView == null) {
            holder = new ViewHolder();
            convertView = mInflater.inflate(R.layout.list_app_item, parent, false);

            // APP INFO
            holder.appName = (TextView) convertView.findViewById(R.id.app_name);
            holder.packageName = (TextView) convertView.findViewById(R.id.app_package);
            holder.iconView = (ImageView) convertView.findViewById(R.id.app_icon);

            // STATUS
            holder.iconState = (ImageView) convertView.findViewById(R.id.state);
            holder.progressBar = (ProgressBar) convertView.findViewById(R.id.progressBar);
            holder.info = (TextView) convertView.findViewById(R.id.waitingState);

            convertView.setTag(holder);
        } else {
            holder = (ViewHolder) convertView.getTag();
        }

        AppItem item = getItem(position);

        String appName = item.getAppName();
        if (appName.length() >= 19){appName = appName.substring(0,19) + "...";}
        holder.appName.setText(appName);
        String pkg = item.getPkg();
        if (pkg.length() >= 25){pkg = pkg.substring(0,25) + "...";}
        holder.iconView.setImageDrawable(item.getAppIcon());

        if (item.wasAnalysed() || !item.isProgressing()) {
            holder.packageName.setText(pkg);

            convertView.setEnabled(true);

            //holder.progressBar.setVisibility(View.GONE);
            holder.info.setVisibility(View.GONE);
            /* */

            holder.iconState.setVisibility(View.VISIBLE);
            if (item.wasAnalysed()) {
                holder.iconState.setImageResource(R.drawable.ic_list_check);
            } else {
                holder.iconState.setImageResource(R.drawable.ic_list_upload);
            }

            holder.progressBar.getLayoutParams().height = 0;
            holder.progressBar.getLayoutParams().width = 0;

        } else if (item.isProgressing()){

            if (item.getLoadingTitle().equals("1/4")){
                holder.packageName.setText(pkg);
            } else {
                holder.packageName.setText("Tap to cancel");
            }

            holder.iconState.setVisibility(View.GONE);

            holder.info.setText(item.getLoadingTitle());

            convertView.setEnabled(false);
            //holder.progressBar.setVisibility(View.VISIBLE);
            holder.progressBar.getLayoutParams().height = 80;
            holder.progressBar.getLayoutParams().width = 80;
            /* */

            holder.info.setVisibility(View.VISIBLE);
        }

        /* */
        holder.progressBar.setVisibility(View.VISIBLE);
        /* */

        return convertView;
    }

    public static class ViewHolder {
        public TextView appName;
        public TextView packageName;
        public TextView info;
        public ImageView iconView;
        public ImageView iconState;
        public ProgressBar progressBar;
    }

}