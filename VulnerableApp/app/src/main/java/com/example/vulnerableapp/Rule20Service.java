package com.example.vulnerableapp;

import android.app.Service;
import android.content.Intent;
import android.os.Handler;
import android.os.IBinder;
import android.os.Messenger;

public class Rule20Service extends Service {
    Messenger mMessenger;

    static class IncomingHandler extends Handler {
        IncomingHandler() {
        }
    }

    public IBinder onBind(Intent intent) {
        Messenger messenger = new Messenger(new IncomingHandler());
        this.mMessenger = messenger;
        return messenger.getBinder();
    }
}
