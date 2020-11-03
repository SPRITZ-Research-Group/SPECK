package com.speck.android.struct;

public class AppDataModel {
    public static final int SUMMARY_TYPE=0;
    public static final int CATEGORY_TYPE=1;
    public static final int ITEM_TYPE=2;
    public static final int DIVIDER_TYPE=3;
    public static final int GENERAL_TYPE=4;
    public static final int PERMISSION_TYPE=5;
    public static final int ACTIVITY_TYPE=6;
    public static final int SERVICE_TYPE=7;
    public static final int PROVIDER_TYPE=8;
    public static final int RECEIVER_TYPE=9;
    public static final int EMPTY_TYPE=10;

    public String data;
    public int type;

    public AppDataModel(int type, String data) {
        this.type=type;
        this.data=data;
    }

}
