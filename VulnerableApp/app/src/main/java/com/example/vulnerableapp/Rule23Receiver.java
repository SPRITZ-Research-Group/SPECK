package com.example.vulnerableapp;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

public class Rule23Receiver extends BroadcastReceiver {
    public void onReceive(Context context, Intent intent) {
        Log.v("BR", "receiver called");
    }
}
