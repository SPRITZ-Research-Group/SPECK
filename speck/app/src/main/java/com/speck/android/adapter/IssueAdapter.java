package com.speck.android.adapter;

import java.util.ArrayList;

import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.ImageView;

import androidx.recyclerview.widget.RecyclerView;

import com.speck.android.R;
import com.speck.android.struct.AppDataModel;

import android.app.AlertDialog;

public class IssueAdapter extends RecyclerView.Adapter {
    private ArrayList<AppDataModel> dataSet;
    Context mContext;
    int total_types;

    /**
     * HOLDERS
     **/
    public static class SummaryTypeViewHolder extends RecyclerView.ViewHolder {
        TextView txtBad;
        TextView txtWarn;
        TextView txtGood;

        LinearLayout layout_bad;
        LinearLayout layout_warn;
        LinearLayout layout_good;

        public SummaryTypeViewHolder(View itemView) {
            super(itemView);

            this.txtBad = (TextView) itemView.findViewById(R.id.summary_bad);
            this.txtGood = (TextView) itemView.findViewById(R.id.summary_good);
            this.txtWarn = (TextView) itemView.findViewById(R.id.summary_warn);
            this.layout_bad = (LinearLayout) itemView.findViewById(R.id.layout_bad);
            this.layout_warn = (LinearLayout) itemView.findViewById(R.id.layout_warn);
            this.layout_good = (LinearLayout) itemView.findViewById(R.id.layout_good);
        }
    }

    public static class CategoryTypeViewHolder extends RecyclerView.ViewHolder {
        TextView txtCategory;

        public CategoryTypeViewHolder(View itemView) {
            super(itemView);

            this.txtCategory = (TextView) itemView.findViewById(R.id.textSeparator);
        }
    }

    public static class ItemTypeViewHolder extends RecyclerView.ViewHolder {
        TextView txtTitle;
        ImageView imgIcon;
        LinearLayout layout;

        public ItemTypeViewHolder(View itemView) {
            super(itemView);

            this.txtTitle = (TextView) itemView.findViewById(R.id.issue_title);
            this.imgIcon = (ImageView) itemView.findViewById(R.id.issue_icon);
            this.layout = (LinearLayout) itemView.findViewById(R.id.item_row);
        }
    }

    public static class DividerTypeViewHolder extends RecyclerView.ViewHolder {
        TextView divider;

        public DividerTypeViewHolder(View itemView) {
            super(itemView);

            this.divider = (TextView) itemView.findViewById(R.id.divider_report);
        }
    }

    public static class GeneralTypeViewHolder extends RecyclerView.ViewHolder {
        TextView title;
        TextView data;
        LinearLayout layout;

        public GeneralTypeViewHolder(View itemView) {
            super(itemView);

            this.title = (TextView) itemView.findViewById(R.id.general_title);
            this.data = (TextView) itemView.findViewById(R.id.general_data);
            this.layout = (LinearLayout) itemView.findViewById(R.id.general_row);
        }
    }

    public static class PermissionTypeViewHolder extends RecyclerView.ViewHolder {
        TextView perm;

        public PermissionTypeViewHolder(View itemView) {
            super(itemView);

            this.perm = (TextView) itemView.findViewById(R.id.perm_item);
        }
    }

    public static class ActivityTypeViewHolder extends RecyclerView.ViewHolder {
        TextView title;
        TextView parent;
        TextView permission;
        Button btn;

        LinearLayout layout_parent;
        LinearLayout layout_perm;

        public ActivityTypeViewHolder(View itemView) {
            super(itemView);

            this.title = (TextView) itemView.findViewById(R.id.activity_title);
            this.parent = (TextView) itemView.findViewById(R.id.activity_parent);
            this.permission = (TextView) itemView.findViewById(R.id.activity_permission);
            this.layout_parent = (LinearLayout) itemView.findViewById(R.id.layout_activity_parent);
            this.layout_perm = (LinearLayout) itemView.findViewById(R.id.layout_activity_permission);
            this.btn = (Button) itemView.findViewById(R.id.button_run_activity);
        }
    }

    public static class ServiceTypeViewHolder extends RecyclerView.ViewHolder {
        TextView title;
        TextView permission;
        TextView exported;

        LinearLayout layout_perm;

        public ServiceTypeViewHolder(View itemView) {
            super(itemView);

            this.title = (TextView) itemView.findViewById(R.id.service_title);
            this.exported = (TextView) itemView.findViewById(R.id.service_exported);
            this.permission = (TextView) itemView.findViewById(R.id.service_permission);
            this.layout_perm = (LinearLayout) itemView.findViewById(R.id.layout_service_permission);
        }
    }

    public static class ProviderTypeViewHolder extends RecyclerView.ViewHolder {
        TextView title;
        TextView read;
        TextView write;
        TextView exported;

        LinearLayout layout_read;
        LinearLayout layout_write;

        public ProviderTypeViewHolder(View itemView) {
            super(itemView);

            this.title = (TextView) itemView.findViewById(R.id.provider_title);
            this.read = (TextView) itemView.findViewById(R.id.provider_read);
            this.write = (TextView) itemView.findViewById(R.id.provider_write);
            this.exported = (TextView) itemView.findViewById(R.id.provider_exported);
            this.layout_read = (LinearLayout) itemView.findViewById(R.id.layout_provider_read);
            this.layout_write = (LinearLayout) itemView.findViewById(R.id.layout_provider_write);
        }
    }

    public static class ReceiverTypeViewHolder extends RecyclerView.ViewHolder {
        TextView title;
        TextView permission;
        TextView exported;

        LinearLayout layout_perm;

        public ReceiverTypeViewHolder(View itemView) {
            super(itemView);

            this.title = (TextView) itemView.findViewById(R.id.receiver_title);
            this.exported = (TextView) itemView.findViewById(R.id.receiver_exported);
            this.permission = (TextView) itemView.findViewById(R.id.receiver_permission);
            this.layout_perm = (LinearLayout) itemView.findViewById(R.id.layout_receiver_permission);
        }
    }

    public static class EmptyTypeViewHolder extends RecyclerView.ViewHolder {
        TextView text;

        public EmptyTypeViewHolder(View itemView) {
            super(itemView);

            this.text = (TextView) itemView.findViewById(R.id.empty_text);
        }
    }

    /**
     * IssueAdapter
     **/

    public IssueAdapter(ArrayList<AppDataModel>data, Context context) {
        this.dataSet = data;
        this.mContext = context;
        if (this.dataSet != null) {
            total_types = this.dataSet.size();
        }
    }

    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {

        View view;
        switch (viewType) {
            case AppDataModel.SUMMARY_TYPE:
                view = LayoutInflater.from(parent.getContext()).inflate(R.layout.type_summary, parent, false);
                return new SummaryTypeViewHolder(view);
            case AppDataModel.CATEGORY_TYPE:
                view = LayoutInflater.from(parent.getContext()).inflate(R.layout.type_category, parent, false);
                return new CategoryTypeViewHolder(view);
            case AppDataModel.ITEM_TYPE:
                view = LayoutInflater.from(parent.getContext()).inflate(R.layout.type_item, parent, false);
                return new ItemTypeViewHolder(view);
            case AppDataModel.DIVIDER_TYPE:
                view = LayoutInflater.from(parent.getContext()).inflate(R.layout.type_divider, parent, false);
                return new ItemTypeViewHolder(view);
            case AppDataModel.GENERAL_TYPE:
                view = LayoutInflater.from(parent.getContext()).inflate(R.layout.type_general, parent, false);
                return new GeneralTypeViewHolder(view);
            case AppDataModel.PERMISSION_TYPE:
                view = LayoutInflater.from(parent.getContext()).inflate(R.layout.type_permission, parent, false);
                return new PermissionTypeViewHolder(view);
            case AppDataModel.ACTIVITY_TYPE:
                view = LayoutInflater.from(parent.getContext()).inflate(R.layout.type_activity, parent, false);
                return new ActivityTypeViewHolder(view);
            case AppDataModel.SERVICE_TYPE:
                view = LayoutInflater.from(parent.getContext()).inflate(R.layout.type_service, parent, false);
                return new ServiceTypeViewHolder(view);
            case AppDataModel.PROVIDER_TYPE:
                view = LayoutInflater.from(parent.getContext()).inflate(R.layout.type_provider, parent, false);
                return new ProviderTypeViewHolder(view);
            case AppDataModel.RECEIVER_TYPE:
                view = LayoutInflater.from(parent.getContext()).inflate(R.layout.type_receiver, parent, false);
                return new ReceiverTypeViewHolder(view);
            case AppDataModel.EMPTY_TYPE:
                view = LayoutInflater.from(parent.getContext()).inflate(R.layout.type_empty, parent, false);
                return new ReceiverTypeViewHolder(view);
        }
        return null;
    }

    @Override
    public int getItemViewType(int position) {

        switch (dataSet.get(position).type) {
            case 0:
                return AppDataModel.SUMMARY_TYPE;
            case 1:
                return AppDataModel.CATEGORY_TYPE;
            case 2:
                return AppDataModel.ITEM_TYPE;
            case 3:
                return AppDataModel.DIVIDER_TYPE;
            case 4:
                return AppDataModel.GENERAL_TYPE;
            case 5:
                return AppDataModel.PERMISSION_TYPE;
            case 6:
                return AppDataModel.ACTIVITY_TYPE;
            case 7:
                return AppDataModel.SERVICE_TYPE;
            case 8:
                return AppDataModel.PROVIDER_TYPE;
            case 9:
                return AppDataModel.RECEIVER_TYPE;
            case 10:
                return AppDataModel.EMPTY_TYPE;
            default:
                return -1;
        }
    }

    @Override
    public void onBindViewHolder(final RecyclerView.ViewHolder holder, final int listPosition) {

        final AppDataModel object = dataSet.get(listPosition);
        if (object != null) {
            switch (object.type) {
                case AppDataModel.SUMMARY_TYPE:
                    ((SummaryTypeViewHolder) holder).txtBad.setText(object.data.split("\\+")[0]);
                    ((SummaryTypeViewHolder) holder).txtWarn.setText(object.data.split("\\+")[1]);
                    ((SummaryTypeViewHolder) holder).txtGood.setText(object.data.split("\\+")[2]);

                    ((SummaryTypeViewHolder) holder).layout_bad.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View view) {
                            AppDataModel object = dataSet.get(holder.getAdapterPosition());
                            String nb = object.data.split("\\+")[0];
                            String txt = " security issues";
                            if (Integer.parseInt(nb) <= 1){ txt = " security issue"; }

                            new AlertDialog.Builder(view.getContext())
                                    .setTitle(nb + txt)
                                    .setMessage("A bad coding practice can represent a threat in terms of security")
                                    .setCancelable(true)
                                    .setNegativeButton("DISMISS", null)
                                    .show();
                        }
                    });

                    ((SummaryTypeViewHolder) holder).layout_warn.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View view) {
                            AppDataModel object = dataSet.get(holder.getAdapterPosition());
                            String nb = object.data.split("\\+")[1];
                            String txt = " warnings";
                            if (Integer.parseInt(nb) <= 1){ txt = " warning"; }

                            new AlertDialog.Builder(view.getContext())
                                    .setTitle(nb + txt)
                                    .setMessage("A warning is a coding practice which can potentially pose a security problem")
                                    .setCancelable(true)
                                    .setNegativeButton("DISMISS", null)
                                    .show();
                        }
                    });

                    ((SummaryTypeViewHolder) holder).layout_good.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View view) {
                            AppDataModel object = dataSet.get(holder.getAdapterPosition());
                            String nb = object.data.split("\\+")[2];
                            String txt = " good practices";
                            if (Integer.parseInt(nb) <= 1){ txt = " good practice"; }

                            new AlertDialog.Builder(view.getContext())
                                    .setTitle(nb + txt)
                                    .setMessage("A good practice is a properly implemented security rule")
                                    .setCancelable(true)
                                    .setNegativeButton("DISMISS", null)
                                    .show();
                        }
                    });
                    break;

                case AppDataModel.CATEGORY_TYPE:
                    ((CategoryTypeViewHolder) holder).txtCategory.setText(object.data);
                    break;

                case AppDataModel.ITEM_TYPE:
                    if (object.data.split("=")[0].equals("criticals")){
                        ((ItemTypeViewHolder) holder).imgIcon.setImageResource(R.drawable.ic_issue_critical);
                    } else if (object.data.split("=")[0].equals("warnings")){
                        ((ItemTypeViewHolder) holder).imgIcon.setImageResource(R.drawable.ic_issue_warning);
                    } else if (object.data.split("=")[0].equals("infos")){
                        ((ItemTypeViewHolder) holder).imgIcon.setImageResource(R.drawable.ic_issue_ok);
                    }

                    ((ItemTypeViewHolder) holder).txtTitle.setText(object.data.split("=")[1].split("@")[0]);

                    ((ItemTypeViewHolder) holder).layout.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View view) {
                            String url = dataSet.get(listPosition).data.split("=")[1].split("@")[2];
                            Intent i = new Intent(Intent.ACTION_VIEW);
                            i.setData(Uri.parse(url));
                            mContext.startActivity(i);
                        }
                    });
                    break;

                case AppDataModel.GENERAL_TYPE:
                    ((GeneralTypeViewHolder) holder).title.setText(object.data.split("@")[0]);

                    String data = object.data.split("@")[1];
                    ((GeneralTypeViewHolder) holder).data.setText(formatString(data,23));

                    ((GeneralTypeViewHolder) holder).layout.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View view) {
                            AppDataModel object = dataSet.get(holder.getAdapterPosition());
                            new AlertDialog.Builder(view.getContext()).setMessage(object.data.split("@")[1]).setTitle(object.data.split("@")[0]).setCancelable(true).setNegativeButton("DISMISS", null).show();
                        }
                    });

                    break;

                case AppDataModel.PERMISSION_TYPE:
                    ((PermissionTypeViewHolder) holder).perm.setText(object.data);
                    break;

                case AppDataModel.ACTIVITY_TYPE:
                    ((ActivityTypeViewHolder) holder).title.setText(object.data.split("@")[0]);
                    ((ActivityTypeViewHolder) holder).parent.setText(formatString(object.data.split("@")[1], 35));
                    ((ActivityTypeViewHolder) holder).permission.setText(formatString(object.data.split("@")[2], 35));

                    ((ActivityTypeViewHolder) holder).layout_perm.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View view) {
                            AppDataModel object = dataSet.get(holder.getAdapterPosition());
                            new AlertDialog.Builder(view.getContext()).setMessage(object.data.split("@")[2]).setTitle("Permission").setCancelable(true).setNegativeButton("DISMISS", null).show();
                        }
                    });

                    ((ActivityTypeViewHolder) holder).layout_parent.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View view) {
                            AppDataModel object = dataSet.get(holder.getAdapterPosition());
                            new AlertDialog.Builder(view.getContext()).setMessage(object.data.split("@")[1]).setTitle("Parent").setCancelable(true).setNegativeButton("DISMISS", null).show();
                        }
                    });

                    if (object.data.split("@")[3].equals("true")) {
                        ((ActivityTypeViewHolder) holder).btn.setTextColor(Color.parseColor("#808080"));
                        ((ActivityTypeViewHolder) holder).btn.setEnabled(true);
                        ((ActivityTypeViewHolder) holder).btn.setOnClickListener(new View.OnClickListener() {
                            @Override
                            public void onClick(View view) {
                                Intent i = new Intent(Intent.ACTION_MAIN);
                                i.setClassName(object.data.split("@")[4], object.data.split("@")[0]);
                                mContext.startActivity(i);
                            }
                        });
                    } else{
                        ((ActivityTypeViewHolder) holder).btn.setTextColor(Color.parseColor("#E8E8E8"));
                        ((ActivityTypeViewHolder) holder).btn.setEnabled(false);
                    }

                    break;

                case AppDataModel.SERVICE_TYPE:
                    ((ServiceTypeViewHolder) holder).title.setText(object.data.split("@")[0]);
                    ((ServiceTypeViewHolder) holder).permission.setText(formatString(object.data.split("@")[1], 35));
                    ((ServiceTypeViewHolder) holder).exported.setText(object.data.split("@")[2]);

                    ((ServiceTypeViewHolder) holder).layout_perm.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View view) {
                            AppDataModel object = dataSet.get(holder.getAdapterPosition());
                            new AlertDialog.Builder(view.getContext()).setMessage(object.data.split("@")[1]).setTitle("Permission").setCancelable(true).setNegativeButton("DISMISS", null).show();
                        }
                    });

                    break;

                case AppDataModel.PROVIDER_TYPE:
                    ((ProviderTypeViewHolder) holder).title.setText(object.data.split("@")[0]);
                    ((ProviderTypeViewHolder) holder).read.setText(formatString(object.data.split("@")[1], 35));
                    ((ProviderTypeViewHolder) holder).write.setText(formatString(object.data.split("@")[2],35));
                    ((ProviderTypeViewHolder) holder).exported.setText(object.data.split("@")[3]);

                    ((ProviderTypeViewHolder) holder).layout_read.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View view) {
                            AppDataModel object = dataSet.get(holder.getAdapterPosition());
                            new AlertDialog.Builder(view.getContext()).setMessage(object.data.split("@")[1]).setTitle("Read permission").setCancelable(true).setNegativeButton("DISMISS", null).show();
                        }
                    });

                    ((ProviderTypeViewHolder) holder).layout_write.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View view) {
                            AppDataModel object = dataSet.get(holder.getAdapterPosition());
                            new AlertDialog.Builder(view.getContext()).setMessage(object.data.split("@")[2]).setTitle("Write permission").setCancelable(true).setNegativeButton("DISMISS", null).show();
                        }
                    });

                    break;

                case AppDataModel.RECEIVER_TYPE:
                    ((ReceiverTypeViewHolder) holder).title.setText(object.data.split("@")[0]);
                    ((ReceiverTypeViewHolder) holder).permission.setText(formatString(object.data.split("@")[1], 35));
                    ((ReceiverTypeViewHolder) holder).exported.setText(object.data.split("@")[2]);

                    ((ReceiverTypeViewHolder) holder).layout_perm.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View view) {
                            AppDataModel object = dataSet.get(holder.getAdapterPosition());
                            new AlertDialog.Builder(view.getContext()).setMessage(object.data.split("@")[1]).setTitle("Permission").setCancelable(true).setNegativeButton("DISMISS", null).show();
                        }
                    });

                    break;

                case AppDataModel.EMPTY_TYPE:
                    break;
            }
        }
    }

    @Override
    public int getItemCount() {
        if (this.dataSet != null) {
            return this.dataSet.size();
        } else {
            return -1;
        }
    }

    private String formatString(String data, int max){
        if (data.length() > max) {
            data = data.substring(0, max) + "...";
        }
        return data;
    }


}

