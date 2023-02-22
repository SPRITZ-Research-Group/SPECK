package com.example.vulnerableapp;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.telephony.SmsManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import android.widget.Toast;
import dalvik.system.DexClassLoader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.URL;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;
import org.apache.http.conn.ssl.AllowAllHostnameVerifier;

public class MainActivity extends Activity {
    private Object runtimeObject;
    private byte[] someData;

    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        try {
            rule1();
            rule5();
            rule6();
            rule8();
            rule9();
            rule11();
            rule12();
            rule14();
            rule19();
            rule22();
            rule24();
            rule25();
            rule26();
            rule29();
            rule30();
            rule31();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void rule1() {
        Intent sendIntent = new Intent();
        sendIntent.setAction("android.intent.action.SEND");
        sendIntent.putExtra("android.intent.extra.TEXT", "some text");
        sendIntent.setType("text/plain");
        startActivity(sendIntent);
    }

    public void rule5() throws Exception {
        HttpURLConnection conn = (HttpURLConnection) new URL("http://example.org").openConnection();
        conn.connect();
        InputStream in = conn.getInputStream();
        in.read(new byte[1024]);
        in.close();
    }

    public void rule6() {
        WebView w = new WebView(this);
        w.getSettings().setJavaScriptEnabled(true);
        w.addJavascriptInterface(new WebAppInterface(this), "Android");
        Intent i = getIntent();
        String url = "https://my-server.org";
        if (i.getStringExtra("URL") != null) {
            url = i.getStringExtra("URL");
        }
        w.loadUrl(url);
        setContentView(w);
    }

    public void rule8() throws Exception {
        FileOutputStream os = openFileOutput("sensitive.txt", Context.MODE_WORLD_READABLE);
        os.write("sensitive information".getBytes());
        os.close();
    }

    public void rule9() {
        File f = new File("sensitive.txt");
        Uri u = Uri.parse("file://" + f.getAbsolutePath());
        Intent i = new Intent();
        i.setAction("random_action");
        i.setData(u);
        i.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        i.setComponent(new ComponentName("random.package", "Receiver"));
        sendBroadcast(i);
    }

    public void rule11() throws Exception {
        String dir = getExternalCacheDir().getAbsolutePath();
        FileOutputStream os = new FileOutputStream(dir + "/" + "sensitive.txt");
        os.write("sensitive information".getBytes());
        os.close();
    }

    public void rule12() {
        SharedPreferences.Editor edit = getPreferences(MODE_WORLD_READABLE|MODE_WORLD_WRITEABLE).edit();
        edit.putString("sensitive", "sensitiveInfo");
        edit.apply();
    }

    public void rule14() throws Exception {
        File dir = getExternalFilesDir(null);
        FileInputStream input = new FileInputStream(dir.getAbsolutePath() + "/in.txt");
        byte[] buf = new byte[1024];
        input.read(buf);
        this.someData = buf;
        input.close();
    }

    public void rule19() {
        new Thread(new Runnable() {
            /* class dev.sime1.vulnerableapplication.MainActivity.AnonymousClass1 */

            public void run() {
                try {
                    InputStream in = new ServerSocket(8080, 1024, InetAddress.getByName("localhost")).accept().getInputStream();
                    for (int res = 0; res != -1; res = in.read(new byte[1024])) {
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }

    public void rule21() {
        SmsManager.getDefault().sendDataMessage("+012345678", null, (short) 8080, "".getBytes(), null, null);
    }

    public void rule22() throws Exception {
        SecretKey k = KeyGenerator.getInstance("AES").generateKey();
        FileOutputStream os = openFileOutput("key.bin", 0);
        os.write(k.getEncoded());
        os.close();
    }

    public void rule24() {
        try {
            this.runtimeObject = new DexClassLoader("external.dex", getCacheDir().getAbsolutePath(), null, getClassLoader()).loadClass("RuntimeClass").newInstance();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void rule25() {
        try {
            URL url = new URL("https://example.org/");
            HttpsURLConnection.setDefaultHostnameVerifier(new AllowAllHostnameVerifier());
            InputStream in = ((HttpsURLConnection) url.openConnection()).getInputStream();
            in.read(new byte[1024]);
            in.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void rule26() throws Exception {
        OutputStream out = ((SSLSocket) SSLSocketFactory.getDefault().createSocket("gmail.com", 443)).getOutputStream();
        out.write("some output".getBytes());
        out.close();
    }

    public void rule29() throws Exception {
        Cipher c = Cipher.getInstance("AES/ECB/NoPadding");
        byte[] buf = "some secret message".getBytes();
        byte[] key = new byte[32];
        c.init(1, new SecretKeySpec(key, 0, key.length, "AES"));
        c.update(buf);
        byte[] enc = c.doFinal();
        FileOutputStream os = openFileOutput("enc.bin", 0);
        os.write(enc);
        os.close();
    }

    public void rule30() throws Exception {
        Cipher c = Cipher.getInstance("AES/CBC/PKCS7PADDING", "BC");
        byte[] buf = "some secret message".getBytes();
        byte[] key = new byte[32];
        c.init(1, new SecretKeySpec(key, 0, key.length, "AES"));
        c.update(buf);
        byte[] enc = c.doFinal();
        FileOutputStream os = openFileOutput("enc.bin", 0);
        os.write(enc);
        os.close();
    }

    public void rule31() {
        if (Build.VERSION.SDK_INT >= 24) {
            createDeviceProtectedStorageContext().moveSharedPreferencesFrom(this, "sensitive");
        }
    }

    public static class WebAppInterface {
        Context mContext;

        WebAppInterface(Context c) {
            this.mContext = c;
        }

        @JavascriptInterface
        public void showToast(String toast) {
            Toast.makeText(this.mContext, toast, Toast.LENGTH_SHORT).show();
        }
    }
}
